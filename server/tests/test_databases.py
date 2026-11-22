"""Accounts, projects, and hardware are stored in three different databases."""

import mongomock

import extensions
from app import create_app
from config import Config


def test_health_names_the_three_databases(client):
    body = client.get("/api/health").get_json()
    assert body["status"] == "ok"
    assert body["usersDb"] == "haas_users"
    assert body["projectsDb"] == "haas_projects"
    assert body["hardwareDb"] == "haas_hardware"
    assert len({body["usersDb"], body["projectsDb"], body["hardwareDb"]}) == 3


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

    assert users["users"].count_documents({}) == 1
    assert projects["users"].count_documents({}) == 0
    assert projects["projects"].find_one({"projectId": "film"})["projectId"] == "film"
    assert users["projects"].find_one({"projectId": "film"}) is None
    hardware = extensions.get_hardware_db()
    assert hardware["hardware_sets"].count_documents({}) == 2
    assert projects["hardware_sets"].count_documents({}) == 0
    assert users["hardware_sets"].count_documents({}) == 0


def test_checkout_history_goes_to_the_hardware_database(client, make_project):
    project_id = make_project()
    response = client.post(
        "/api/hardware/checkout",
        json={"projectId": project_id, "setId": "HWSet1", "quantity": 1},
    )
    assert response.status_code == 200

    hardware = extensions.get_hardware_db()
    projects = extensions.get_projects_db()
    assert hardware["checkout_records"].count_documents({"projectId": project_id}) == 1
    assert projects["checkout_records"].count_documents({}) == 0
    # The project's own tally stays with the project.
    assert projects["projects"].find_one({"projectId": project_id})["checkedOut"] == {"HWSet1": 1}


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
    monkeypatch.setattr(Config, "HARDWARE_MONGO_URI", "mongodb://hardware.example:27017")
    monkeypatch.setattr(Config, "USERS_DB_NAME", "haas_users")
    monkeypatch.setattr(Config, "PROJECTS_DB_NAME", "haas_projects")
    monkeypatch.setattr(Config, "HARDWARE_DB_NAME", "haas_hardware")

    create_app()

    assert opened == [
        "mongodb://users.example:27017",
        "mongodb://projects.example:27017",
        "mongodb://hardware.example:27017",
    ]
    assert extensions.get_users_db().name == "haas_users"
    assert extensions.get_projects_db().name == "haas_projects"
    assert extensions.get_hardware_db().name == "haas_hardware"
    clients = {id(db.client) for db in (
        extensions.get_users_db(), extensions.get_projects_db(), extensions.get_hardware_db()
    )}
    assert len(clients) == 3


def test_one_uri_shares_one_connection_across_three_databases(client):
    users = extensions.get_users_db()
    projects = extensions.get_projects_db()
    hardware = extensions.get_hardware_db()
    assert users.client is projects.client is hardware.client
    assert {users.name, projects.name, hardware.name} == {
        "haas_users", "haas_projects", "haas_hardware"
    }
