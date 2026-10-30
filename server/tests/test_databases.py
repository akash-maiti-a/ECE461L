"""Accounts and projects are stored in different databases."""

import mongomock

import extensions
from app import create_app
from config import Config


def test_health_names_the_two_databases(client):
    body = client.get("/api/health").get_json()
    assert body["status"] == "ok"
    assert body["usersDb"] == "haas_users"
    assert body["projectsDb"] == "haas_projects"
    assert body["usersDb"] != body["projectsDb"]


def test_signup_and_projects_write_to_different_databases(client):
    created = client.post(
        "/api/projects",
        json={"projectId": "film", "name": "Film", "description": "A short"},
    )
    assert created.status_code == 201

    users = extensions.get_users_db()
    projects = extensions.get_projects_db()
    assert users.name == "haas_users"
    assert projects.name == "haas_projects"
    # Same cluster by default, so one connection serves both databases.
    assert users.client is projects.client

    assert users["users"].find_one({"userid": "alice"})["userid"] == "alice"
    assert projects["users"].find_one({"userid": "alice"}) is None
    assert projects["projects"].find_one({"projectId": "film"})["projectId"] == "film"
    assert users["projects"].find_one({"projectId": "film"}) is None
    assert projects["hardware_sets"].count_documents({}) == 2
    assert users["hardware_sets"].count_documents({}) == 0


def test_checkout_history_stays_with_projects(client, make_project):
    project_id = make_project()
    response = client.post(
        "/api/hardware/checkout",
        json={"projectId": project_id, "setId": "HWSet1", "quantity": 1},
    )
    assert response.status_code == 200

    users = extensions.get_users_db()
    projects = extensions.get_projects_db()
    assert projects["checkout_records"].count_documents({"projectId": project_id}) == 1
    assert users["checkout_records"].count_documents({}) == 0


def test_different_uris_open_two_connections(monkeypatch):
    opened = []

    class RecordingClient(mongomock.MongoClient):
        def __init__(self, uri, *args, **kwargs):
            opened.append(uri)
            super().__init__()

    monkeypatch.setattr(extensions, "MongoClient", RecordingClient)
    monkeypatch.setattr(Config, "USE_MOCK_DB", False)
    monkeypatch.setattr(Config, "MONGO_URI", "mongodb://localhost:27017")
    monkeypatch.setattr(Config, "USERS_MONGO_URI", "mongodb://users.example:27017")
    monkeypatch.setattr(Config, "PROJECTS_MONGO_URI", "mongodb://projects.example:27017")
    monkeypatch.setattr(Config, "USERS_DB_NAME", "haas_users")
    monkeypatch.setattr(Config, "PROJECTS_DB_NAME", "haas_projects")

    create_app()

    assert opened == [
        "mongodb://users.example:27017",
        "mongodb://projects.example:27017",
    ]
    assert extensions.get_users_db().name == "haas_users"
    assert extensions.get_projects_db().name == "haas_projects"
    assert extensions.get_users_db().client is not extensions.get_projects_db().client
