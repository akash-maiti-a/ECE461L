"""Every project is open: anyone signed in can see it, only the crew can use it."""

from tests.test_sharing import make_project, signup


def test_anyone_can_see_any_project_but_only_the_crew_can_use_it(app, client):
    make_project(client)
    bob = signup(app, "bob")

    assert bob.get("/api/projects").get_json() == [
        {"projectId": "film", "name": "Film", "ownerUserid": "alice", "members": ["alice"]}
    ]
    seen = bob.get("/api/projects/film")
    assert seen.status_code == 200
    assert seen.get_json()["description"] == "A short"
    assert "open" not in seen.get_json()

    checkout = bob.post(
        "/api/hardware/checkout",
        json={"projectId": "film", "setId": "HWSet1", "quantity": 1},
    )
    assert checkout.status_code == 403
    assert bob.post("/api/projects/film/members", json={"userid": "bob"}).status_code == 403


def test_there_is_no_switch_to_close_a_project(app, client):
    make_project(client)
    assert client.patch("/api/projects/film", json={"open": False}).status_code == 405
