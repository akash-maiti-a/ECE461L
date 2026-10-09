"""Shared PyTest fixtures.

We swap the real pymongo.MongoClient for mongomock's in-memory
drop-in replacement, so tests run instantly with no real MongoDB
instance required -- useful for CI and for any teammate's laptop.
"""

import sys
from pathlib import Path

import mongomock
import pytest

# Allow "import app", "import extensions", etc. to resolve when pytest
# is run from the repo root instead of from inside server/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import extensions  # noqa: E402
from app import create_app  # noqa: E402


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(extensions, "MongoClient", mongomock.MongoClient)
    flask_app = create_app()
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()
