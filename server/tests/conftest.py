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
from config import Config  # noqa: E402


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(extensions, "MongoClient", mongomock.MongoClient)
    # Ignore any Atlas URI in .env: a mongodb+srv:// URI makes even mongomock
    # do a DNS lookup, which slows every test and needs the network.
    monkeypatch.setattr(Config, "MONGO_URI", "mongodb://localhost:27017/haas_db")
    monkeypatch.setattr(Config, "USERS_MONGO_URI", None)
    monkeypatch.setattr(Config, "PROJECTS_MONGO_URI", None)
    monkeypatch.setattr(Config, "USERS_DB_NAME", "haas_users")
    monkeypatch.setattr(Config, "PROJECTS_DB_NAME", "haas_projects")
    flask_app = create_app()
    yield flask_app


@pytest.fixture
def client(app):
    """A browser signed in as alice (the test client keeps the cookie)."""
    browser = app.test_client()
    browser.post("/api/auth/signup", json={"userid": "alice", "password": "alice-pass"})
    return browser


@pytest.fixture
def make_project(client):
    """Create a project through the API and return its projectId."""

    def _make(project_id="proj-1"):
        response = client.post(
            "/api/projects",
            json={
                "projectId": project_id,
                "name": f"Project {project_id}",
                "description": "Test project",
            },
        )
        assert response.status_code == 201
        return project_id

    return _make
