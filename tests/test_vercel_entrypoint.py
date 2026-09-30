import importlib
import sys

import pytest
from flask import Flask


def _load_entrypoint():
    sys.modules.pop("app", None)
    return importlib.import_module("app")


def test_entrypoint_exposes_flask_app(monkeypatch):
    monkeypatch.setenv("KNOCKKNOCK_SECRET_KEY", "test-secret")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    entrypoint = _load_entrypoint()

    assert isinstance(entrypoint.app, Flask)
    assert entrypoint.app.secret_key == "test-secret"


def test_entrypoint_requires_secret_key(monkeypatch):
    monkeypatch.delenv("KNOCKKNOCK_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="KNOCKKNOCK_SECRET_KEY"):
        _load_entrypoint()
