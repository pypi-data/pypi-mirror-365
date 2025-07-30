"""
Tests for batch and web (HTTP) modes of operation.
Run with:
    pytest --cov=joblet --cov-report=term-missing
"""

import json
import os
import sys
import tempfile
import types
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure joblet modules are importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from joblet import cli, http
from joblet.common import Context, run_handler
from cloudevents.pydantic import CloudEvent

# Import the test handler from testapp.py
testapp_path = Path(__file__).parent.parent / "testapp.py"
spec = types.ModuleType("testapp")
with open(testapp_path) as f:
    code = f.read()
exec(code, spec.__dict__)
handle = spec.handle
CloudEventModel = spec.CloudEvent


def make_sample_event() -> dict:
    return {
        "specversion": "1.0",
        "type": "test.type",
        "source": "/test/source",
        "id": "1234",
        "data": {"foo": "bar"},
        "myextension1": "baz",
    }


def test_batch_mode(monkeypatch):
    """Test running the handler in batch mode (simulating CLI logic)."""
    event = make_sample_event()
    context = Context(None, CloudEventModel(**event))
    result = run_handler(context, handle)
    assert isinstance(result, CloudEvent)
    assert result.data == {"ceva": "altceva"}


def test_web_mode():
    """Test running the handler in web (HTTP) mode using FastAPI TestClient."""
    client = TestClient(http.app)
    event = make_sample_event()
    headers = {
        "ce-specversion": "1.0",
        "ce-type": event["type"],
        "ce-source": event["source"],
        "ce-id": event["id"],
        "content-type": "application/json",
        "ce-myextension1": event["myextension1"],
    }
    response = client.post("/", headers=headers, json=event["data"])
    assert response.status_code == 200
    assert response.json()["data"] == {"ceva": "altceva"}


def test_healthz_and_readyz():
    """Test Kubernetes health check endpoints."""
    client = TestClient(http.app)
    for path in ["/healthz", "/readyz"]:
        response = client.get(path)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
