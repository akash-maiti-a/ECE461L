"""Joining a project by typing its ID. There are no invites."""

import extensions


def signup(app, userid, password="password1"):
    browser = app.test_client()
    response = browser.post("/api/auth/signup", json={"userid": userid, "password": password})
    assert response.status_code == 201
    return browser


def make_project(client, project_id="film"):
    response = client.post(
        "/api/projects",
        json={"projectId": project_id, "name": "Film", "description": "A short"},
    )
    assert response.status_code == 201
    return response


def checkout(browser, project_id="film"):
    return browser.post(
        "/api/hardware/checkout",
        json={"projectId": project_id, "setId": "HWSet1", "quantity": 1},
    )


def test_you_cannot_use_a_project_until_you_join_it(app, client):
    make_project(client)
    bob = signup(app, "bob")

    assert bob.get("/api/projects").get_json() == []
    hidden = bob.get("/api/projects/film")
    assert hidden.status_code == 403
    assert "Join a project" in hidden.get_json()["error"]
    assert checkout(bob).status_code == 403
    # The shelf did not move.
    hardware = {hw["setId"]: hw for hw in client.get("/api/hardware").get_json()}
    assert hardware["HWSet1"]["available"] == 10


def test_entering_a_matching_project_id_lets_you_in(app, client):
    make_project(client)
    bob = signup(app, "bob")

    joined = bob.post("/api/projects/film/join")
    assert joined.status_code == 200
    assert joined.get_json()["members"] == ["alice", "bob"]
    assert joined.get_json()["description"] == "A short"

    assert bob.get("/api/projects").get_json() == [
        {"projectId": "film", "name": "Film", "ownerUserid": "alice", "members": ["alice", "bob"]}
    ]
    assert bob.get("/api/projects/film").status_code == 200
    assert checkout(bob).status_code == 200


def test_an_id_that_matches_no_project_is_rejected(app, client):
    make_project(client)
    bob = signup(app, "bob")

    missing = bob.post("/api/projects/nope/join")
    assert missing.status_code == 404
    assert missing.get_json()["error"] == 'No project has the ID "nope".'
    # IDs match exactly.
    assert bob.post("/api/projects/FILM/join").status_code == 404
    assert bob.get("/api/projects").get_json() == []


def test_joining_twice_or_joining_your_own_project_changes_nothing(app, client):
    make_project(client)
    bob = signup(app, "bob")

    assert client.post("/api/projects/film/join").get_json()["members"] == ["alice"]
    bob.post("/api/projects/film/join")
    again = bob.post("/api/projects/film/join")
    assert again.status_code == 200
    assert again.get_json()["members"] == ["alice", "bob"]


def test_joining_needs_you_signed_in(app, client):
    make_project(client)
    assert app.test_client().post("/api/projects/film/join").status_code == 401


def test_there_are_no_invite_or_user_search_endpoints(app, client):
    make_project(client)
    signup(app, "bob")
    assert client.post("/api/projects/film/members", json={"userid": "bob"}).status_code in (404, 405)
    assert client.delete("/api/projects/film/members/bob").status_code in (404, 405)
    assert client.get("/api/users?q=bo").status_code == 404


def test_projects_stored_before_members_existed_keep_their_owner_first(app, client):
    extensions.get_projects_db()["projects"].insert_one(
        {
            "projectId": "old",
            "name": "Old shoot",
            "description": "Created before members existed",
            "ownerUserid": "alice",
            "checkedOut": {},
        }
    )
    old = client.get("/api/projects").get_json()[0]
    assert old["members"] == ["alice"]

    bob = signup(app, "bob")
    assert checkout(bob, "old").status_code == 403
    assert bob.post("/api/projects/old/join").get_json()["members"] == ["alice", "bob"]
    assert checkout(bob, "old").status_code == 200
