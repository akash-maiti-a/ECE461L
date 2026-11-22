"""Moving hardware into its own database keeps a live deployment's counts.

These set up what an existing deployment looks like (hardware sets and
checkout history in the projects database, kits checked out) and start
the app against it.
"""

import mongomock
import pytest

import extensions
from app import create_app
from config import Config


@pytest.fixture
def cluster(monkeypatch):
    """One in-memory cluster shared by every connection the app opens."""
    shared = mongomock.MongoClient()
    monkeypatch.setattr(extensions, "MongoClient", lambda *args, **kwargs: shared)
    monkeypatch.setattr(Config, "USE_MOCK_DB", False)
    monkeypatch.setattr(Config, "MONGO_URI", "mongodb://localhost:27017")
    for name in ("USERS_MONGO_URI", "PROJECTS_MONGO_URI", "HARDWARE_MONGO_URI"):
        monkeypatch.setattr(Config, name, None)
    monkeypatch.setattr(Config, "USERS_DB_NAME", "haas_users")
    monkeypatch.setattr(Config, "PROJECTS_DB_NAME", "haas_projects")
    monkeypatch.setattr(Config, "HARDWARE_DB_NAME", "haas_hardware")
    return shared


def seed_old_layout(cluster):
    """A deployment from before the move: 5 camera kits out to film-01."""
    projects = cluster["haas_projects"]
    projects["hardware_sets"].insert_many([
        {"setId": "HWSet1", "name": "Camera kits", "capacity": 10, "available": 5, "contents": []},
        {"setId": "HWSet2", "name": "Audio and lighting kits", "capacity": 8, "available": 8, "contents": []},
    ])
    projects["checkout_records"].insert_one(
        {"projectId": "film-01", "setId": "HWSet1", "quantity": 5, "action": "checkout"}
    )
    projects["projects"].insert_one({
        "projectId": "film-01", "name": "Film", "description": "d",
        "ownerUserid": "alice", "members": ["alice"], "checkedOut": {"HWSet1": 5},
    })


def counts(cluster):
    sets = cluster["haas_hardware"]["hardware_sets"].find({}, {"_id": 0})
    return {s["setId"]: (s["available"], s["capacity"]) for s in sets}


def test_live_counts_and_history_move_to_the_hardware_database(cluster):
    seed_old_layout(cluster)

    create_app()

    assert counts(cluster) == {"HWSet1": (5, 10), "HWSet2": (8, 8)}
    assert cluster["haas_hardware"]["checkout_records"].count_documents({}) == 1


def test_the_old_copies_are_left_in_place(cluster):
    seed_old_layout(cluster)

    create_app()

    assert cluster["haas_projects"]["hardware_sets"].count_documents({}) == 2
    assert cluster["haas_projects"]["checkout_records"].count_documents({}) == 1


def test_a_project_can_return_its_kits_without_passing_capacity(cluster):
    seed_old_layout(cluster)
    browser = create_app().test_client()
    browser.post("/api/auth/signup", json={"userid": "alice", "password": "alice-pass"})

    response = browser.post(
        "/api/hardware/checkin", json={"projectId": "film-01", "setId": "HWSet1", "quantity": 5}
    )

    assert response.status_code == 200
    assert counts(cluster)["HWSet1"] == (10, 10)


def test_restarting_copies_nothing_twice_and_keeps_new_counts(cluster):
    seed_old_layout(cluster)
    create_app()
    # A kit moves after the switch; only the hardware database sees it.
    cluster["haas_hardware"]["hardware_sets"].update_one(
        {"setId": "HWSet1"}, {"$set": {"available": 7}}
    )

    create_app()  # e.g. a redeploy, or the second server worker starting

    assert counts(cluster) == {"HWSet1": (7, 10), "HWSet2": (8, 8)}
    assert cluster["haas_hardware"]["hardware_sets"].count_documents({}) == 2
    assert cluster["haas_hardware"]["checkout_records"].count_documents({}) == 1


def test_a_brand_new_deployment_starts_with_full_shelves(cluster):
    create_app()

    assert counts(cluster) == {"HWSet1": (10, 10), "HWSet2": (8, 8)}
