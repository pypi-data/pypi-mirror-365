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

import functools
import requests
import logging
import os
import sys

from cloudevents.pydantic import CloudEvent
from fastapi import Request
from typing import Optional
from cloudevents.conversion import to_structured

from pydantic import Field, ValidationError

logger = logging.getLogger(__name__)


class JobLetException(Exception):
    pass


class JobLetValidationException(JobLetException):
    pass


class InputValidationError(JobLetValidationException):
    pass


class OutputValidationError(JobLetValidationException):
    pass


def _validate_input_event(context: "Context", input_model: type) -> CloudEvent:
    try:
        return input_model.model_validate(context.cloud_event.model_dump())
    except ValidationError as e:
        logger.error(f"Input validation failed: {e}")
        raise InputValidationError(e) from e


def _create_new_context(request: Optional[Request], event: CloudEvent) -> "Context":
    return Context(request, event)


def _construct_output_event(
    data, return_model: type, event_source: Optional[str], event_type: Optional[str]
) -> CloudEvent:
    kws = {}
    if event_source is not None:
        kws["source"] = event_source
    if event_type is not None:
        kws["type"] = event_type
    try:
        cl_event = return_model(data=data, **kws)
        return return_model.model_validate(cl_event)
    except ValidationError as e:
        logger.error(f"Output validation failed: {e}")
        raise OutputValidationError(e) from e


def event(
    _func: callable = None,
    *,
    event_type: str = "joblet.event",
    event_source: str = "/joblet/function",
    return_model: type = CloudEvent,
    input_model: type = CloudEvent,
) -> callable:
    """
    Provides an @event decorator compatible with parliament @event
    :return:
    """

    def decorator(func: callable) -> callable:
        @functools.wraps(func)
        def wrapper(context: Context, *args, **kwargs):
            evnt = _validate_input_event(context, input_model)
            new_context = _create_new_context(context.request, evnt)
            data = func(new_context, *args, **kwargs)
            if isinstance(data, CloudEvent):
                return data
            elif data is None:
                return None
            else:
                return _construct_output_event(
                    data, return_model, event_source, event_type
                )

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


class Context:
    request: Optional[Request] = None
    cloud_event: Optional[CloudEvent] = None

    def __init__(
        self, request: Optional[Request], cloud_event: Optional[CloudEvent] = None
    ) -> None:
        self.request = request
        self.cloud_event = cloud_event


def run_handler(
    context: Context,
    func: callable,
    k_sink: Optional[str] = None,
    oidc_token: Optional[str] = None,
    oidc_token_func: Optional[callable] = None,
    send_to_sink: Optional[bool] = None,
) -> CloudEvent:
    """
    Run handler for user function.
    :param context: Context object
    :param func: Function to be executed
    :param k_sink: Destination for the returned event
    :param oidc_token: OIDC Token to be used by the function. If not provided, the function will try to fetch it from the provided callback. If no callback is provided, the function will try to send without authentication
    :param oidc_token_func: Callback to fetch OIDC token. If not provided, the function will try to fetch it from the provided callback. If no callback is provided, the function will try to send without authentication. This callback will be called with no arguments.
    :param send_to_sink: If True, send the returned event to k_sink. If False, do not send. If None, controlled by the JOBLET_SEND_TO_SINK environment variable (default: False).
    :return:
    """
    rez = func(context)
    logger.info(f"Handler returned: {rez}")
    if send_to_sink is None:
        send_to_sink = os.environ.get("JOBLET_SEND_TO_SINK", "false").lower() in (
            "true",
            "1",
            "yes",
            "on",
        )
    if send_to_sink and k_sink is not None:
        if oidc_token is None:
            logger.info("No OIDC token provided")
            if oidc_token_func is not None:
                logger.info("Fetching OIDC token from provided callback")
                oidc_token = oidc_token_func()
            else:
                logger.info("No OIDC token callback provided")
        if oidc_token is None:
            logger.warning("No OIDC token found")
        headers = {}
        if oidc_token:
            headers["Authorization"] = f"Bearer {oidc_token}"
        resp_headers, body = to_structured(rez)
        headers.update(resp_headers)
        logger.info(f"Sending event to {k_sink}")
        logger.debug(f"Event body: {body}")
        try:
            r = requests.post(
                k_sink,
                headers=headers,
                data=body,
            )
            r.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send event to sink: {e}")
            raise
    return rez


def setup_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s\t[%(levelname)-10s]\t%(name)s:\t%(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )
