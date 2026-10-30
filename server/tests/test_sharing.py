"""Sharing a project with other accounts, and suggesting those accounts."""

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


def test_only_the_crew_can_see_and_use_a_project(app, client):
    make_project(client)
    bob = signup(app, "bob")

    assert bob.get("/api/projects").get_json() == []
    denied = bob.get("/api/projects/film")
    assert denied.status_code == 403
    assert denied.get_json()["error"] == "This project isn't shared with you."

    checkout = bob.post(
        "/api/hardware/checkout",
        json={"projectId": "film", "setId": "HWSet1", "quantity": 1},
    )
    assert checkout.status_code == 403
    # The shelf did not move.
    hardware = {hw["setId"]: hw for hw in client.get("/api/hardware").get_json()}
    assert hardware["HWSet1"]["available"] == 10

    shared = client.post("/api/projects/film/members", json={"userid": "bob"})
    assert shared.status_code == 200
    assert shared.get_json()["members"] == ["alice", "bob"]

    assert bob.get("/api/projects").get_json() == [
        {
            "projectId": "film",
            "name": "Film",
            "ownerUserid": "alice",
            "members": ["alice", "bob"],
        }
    ]
    assert bob.get("/api/projects/film").status_code == 200
    assert (
        bob.post(
            "/api/hardware/checkout",
            json={"projectId": "film", "setId": "HWSet1", "quantity": 1},
        ).status_code
        == 200
    )


def test_share_uses_the_stored_userid_and_rejects_unknown_or_duplicate(app, client):
    make_project(client)
    signup(app, "bob")

    missing = client.post("/api/projects/film/members", json={"userid": "nobody"})
    assert missing.status_code == 404
    assert missing.get_json()["error"] == 'No account has the user ID "nobody".'

    shared = client.post("/api/projects/film/members", json={"userid": "BoB"})
    assert shared.status_code == 200
    assert shared.get_json()["members"] == ["alice", "bob"]

    again = client.post("/api/projects/film/members", json={"userid": "bob"})
    assert again.status_code == 409
    assert again.get_json()["error"] == "bob is already on this project."

    operator = client.post("/api/projects/film/members", json={"userid": {"$ne": None}})
    assert operator.status_code == 400
    assert operator.get_json()["error"] == "Enter a user ID."


def test_someone_off_the_project_cannot_share_it(app, client):
    make_project(client)
    carol = signup(app, "carol")
    signup(app, "bob")

    response = carol.post("/api/projects/film/members", json={"userid": "bob"})
    assert response.status_code == 403
    assert client.get("/api/projects/film").get_json()["members"] == ["alice"]


def test_owner_can_remove_a_member_but_not_themselves(app, client):
    make_project(client)
    bob = signup(app, "bob")
    assert client.post("/api/projects/film/members", json={"userid": "bob"}).status_code == 200

    owner = client.delete("/api/projects/film/members/alice")
    assert owner.status_code == 400
    assert owner.get_json()["error"] == "The owner stays on the project."

    removed = client.delete("/api/projects/film/members/bob")
    assert removed.status_code == 200
    assert removed.get_json()["members"] == ["alice"]
    assert bob.get("/api/projects/film").status_code == 403

    absent = client.delete("/api/projects/film/members/bob")
    assert absent.status_code == 404


def test_user_search_suggests_existing_accounts(app, client):
    signup(app, "bob")
    signup(app, "bobby")
    signup(app, "a.b")
    signup(app, "axb")

    matches = client.get("/api/users?q=bo")
    assert matches.status_code == 200
    assert matches.get_json() == [{"userid": "bob"}, {"userid": "bobby"}]
    assert "password_hash" not in matches.get_json()[0]

    assert client.get("/api/users?q=BO").get_json() == [{"userid": "bob"}, {"userid": "bobby"}]
    # "." is literal, so it does not also match "axb".
    assert client.get("/api/users?q=a.").get_json() == [{"userid": "a.b"}]
    assert client.get("/api/users").get_json() == []
    assert client.get("/api/users?q=").get_json() == []

    signed_out = app.test_client()
    assert signed_out.get("/api/users?q=bo").status_code == 401


def test_projects_stored_before_sharing_stay_with_their_owner(app, client):
    extensions.get_db()["projects"].insert_one(
        {
            "projectId": "old",
            "name": "Old shoot",
            "description": "Created before members existed",
            "ownerUserid": "alice",
            "checkedOut": {},
        }
    )
    listed = client.get("/api/projects").get_json()
    old = next(project for project in listed if project["projectId"] == "old")
    assert old["members"] == ["alice"]

    bob = signup(app, "bob")
    assert bob.get("/api/projects/old").status_code == 403

    shared = client.post("/api/projects/old/members", json={"userid": "bob"})
    assert shared.status_code == 200
    assert shared.get_json()["members"] == ["alice", "bob"]
    assert bob.get("/api/projects/old").status_code == 200
