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


from fastapi import FastAPI

app = FastAPI()


@app.get("/health/liveness")
def healthz() -> dict:
    """Kubernetes liveness probe endpoint."""
    return {"status": "ok"}


@app.get("/health/readiness")
def readyz() -> dict:
    """Kubernetes readiness probe endpoint."""
    return {"status": "ok"}
