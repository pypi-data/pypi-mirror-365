#!/usr/bin/env python

# Copyright 2025 Y22 Laboratories SA
# Copyright 2025 West Univerity of Timisoara
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import json
import sys
import os
import importlib
import logging


from joblet.common import Context, InputValidationError, OutputValidationError
from joblet.common import run_handler, setup_logging
from joblet.http import app
from cloudevents.pydantic import from_http, from_dict
from cloudevents.conversion import to_structured

import uvicorn
from fastapi import Request, Response


setup_logging()

logger = logging.getLogger(__name__)


def import_function_from_module(module_path: str) -> callable:
    if ":" not in module_path:
        logger.warning("Callable not specified. Using `handle`")
        module_name = module_path
        func_name = "handle"
    else:
        module_name, func_name = module_path.split(":", 1)

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        logger.error(f"Can't import module '{module_name}': {e}")
        raise ImportError(f"Can't import module '{module_name}': {e}")

    try:
        func = getattr(module, func_name)
    except AttributeError:
        logger.error(f"Failed to find callable {func_name} from module {module_name}")
        raise ImportError(
            f"Failed to find callable {func_name} from module {module_name}"
        )

    if not callable(func):
        logger.error(f"'Symbol {func_name}' from '{module_name}' is not callable")
        raise TypeError(f"'Symbol {func_name}' from '{module_name}' is not callable")
    return func


def main() -> None:
    event_path = os.environ.get("JOBLET_EVENT_PATH", None)
    parser = argparse.ArgumentParser(description="Run CloudEvent handler")
    parser.add_argument(
        "--module", required=True, help="Format: 'module:callable' ex: myapp.foo:main"
    )
    parser.add_argument("--path", help="Append this path to sys.path")
    joblet_batch = os.environ.get("JOBLET_BATCH", "False").lower() in (
        "true",
        "on",
        "yes",
    )
    k_execution_mode = os.environ.get("K_EXECUTION_MODE", None)
    if k_execution_mode is not None:
        if k_execution_mode == "batch":
            logger.info(
                f"KNative asked for batch execution mode. Joblet mode is set to {joblet_batch}"
            )
            joblet_batch = True
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run in batch mode (default: False)",
        default=joblet_batch,
    )
    parser.add_argument(
        "--event-path",
        type=str,
        help="Path to CloudEvent JSON  event file. Valid only for batch mode",
        default=event_path,
    )
    parser.add_argument(
        "--destination-sink",
        type=str,
        help="Destination SINK",
        default=os.environ.get("K_SINK", None),
    )
    parser.add_argument(
        "--http-port",
        type=int,
        help="HTTP Listen port. Valid only for HTTP mode",
        default=8080,
    )

    parser.add_argument(
        "--http-host",
        type=str,
        help="Host to listen on. Valid only for HTTP mode",
        default="0.0.0.0",
    )

    parser.add_argument(
        "--send-to-sink",
        dest="send_to_sink",
        action="store_true",
        help="Send the returned event to the configured k_sink (overrides JOBLET_SEND_TO_SINK)",
        default=None,
    )
    parser.add_argument(
        "--no-send-to-sink",
        dest="send_to_sink",
        action="store_false",
        help="Do not send the returned event to the configured k_sink (overrides JOBLET_SEND_TO_SINK)",
    )

    args = parser.parse_args()

    if not args.batch and args.event_path:
        logger.error("--event-path can be used only with --batch")
        parser.error("--event-path can be used only with --batch")

    if args.path:
        abs_path = os.path.abspath(args.path)
        sys.path.insert(0, abs_path)

    try:
        func = import_function_from_module(args.module)
    except Exception as e:
        logger.error(f"Failed to import: {e}")
        sys.exit(2)

    kws = {"k_sink": os.environ.get("K_SINK", None)}

    token_path = os.environ.get("EOCUBE_K8S_OIDC_TOKEN_PATH", None)
    if token_path is not None:
        kws["oidc_token_func"] = lambda: open(token_path).read()

    try:
        result = None
        if args.batch:
            logger.info("Running in batch mode")
            try:
                if args.event_path is not None:
                    event_path = args.event_path
                if event_path is None:
                    event_path = "/etc/jobsink-event/event"
                with open(event_path) as f:
                    event = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load event file: {e}")
                sys.exit(1)
            context = Context(None, from_dict(event))
            try:
                rez = run_handler(context, func, **kws, send_to_sink=args.send_to_sink)
            except Exception as e:
                logger.exception(f"Error running handler in batch mode: {e}")
                sys.exit(1)
        else:
            logger.info("Running in HTTP mode")

            @app.post("/")
            async def handle(request: Request) -> Response:
                body = await request.body()
                req_headers = dict(request.headers)
                try:
                    event = from_http(req_headers, body)
                except Exception as e:
                    logger.error(f"Failed to parse CloudEvent: {e}")
                    return Response(status_code=400, content=str(e))
                context = Context(request, event)
                try:
                    del kws["k_sink"]  # Not needed as we return the event by ourselves
                    rez = run_handler(
                        context, func, **kws, send_to_sink=args.send_to_sink
                    )
                except InputValidationError as e:
                    logger.error(f"Input validation error: {e}")
                    return Response(status_code=400, content=str(e))
                except OutputValidationError as e:
                    logger.exception(f"Failed to validate output: {e}")
                    return Response(status_code=500, content=str(e))
                except Exception as e:
                    logger.exception(f"Unhandled exception: {e}")
                    return Response(status_code=500, content=str(e))
                resp_headers, body = to_structured(rez)
                return Response(headers=resp_headers, content=body)

            uvicorn.run(app, port=args.http_port, host=args.http_host)

    except Exception as e:
        logger.exception(f"Failed to run: {e}")
        raise e


if __name__ == "__main__":
    main()
