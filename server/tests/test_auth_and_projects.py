def test_signup_then_duplicate_is_rejected(app):
    client = app.test_client()
    first = client.post("/api/auth/signup", json={"userid": "alice", "password": "secret123"})
    assert first.status_code == 201

    second = client.post("/api/auth/signup", json={"userid": "alice", "password": "other-pass"})
    assert second.status_code == 409
    assert second.get_json()["error"] == "That user ID is taken. Try another one."


def test_signin_requires_correct_password(client):
    client.post("/api/auth/signout")
    client.post("/api/auth/signup", json={"userid": "bob", "password": "correct-horse"})

    good = client.post("/api/auth/signin", json={"userid": "bob", "password": "correct-horse"})
    assert good.status_code == 200
    assert good.get_json() == {"userid": "bob"}

    bad = client.post("/api/auth/signin", json={"userid": "bob", "password": "wrong"})
    assert bad.status_code == 401
    assert bad.get_json()["error"] == "User ID or password is incorrect."


def test_signup_requires_both_fields(client):
    response = client.post("/api/auth/signup", json={"userid": "carol"})
    assert response.status_code == 400


def test_create_and_get_project(client):
    body = {
        "projectId": "proj-1",
        "name": "Demo Project",
        "description": "A test project",
    }
    create = client.post("/api/projects", json=body)
    assert create.status_code == 201
    # New projects start with nothing checked out.
    assert create.get_json() == {
        **body,
        "ownerUserid": "alice",
        "members": ["alice"],
        "checkedOut": {},
    }

    get = client.get("/api/projects/proj-1")
    assert get.status_code == 200
    assert get.get_json() == {
        **body,
        "ownerUserid": "alice",
        "members": ["alice"],
        "checkedOut": {},
    }


def test_create_project_duplicate_id_rejected(client):
    body = {
        "projectId": "proj-2",
        "name": "First",
        "description": "desc",
    }
    assert client.post("/api/projects", json=body).status_code == 201

    duplicate = client.post("/api/projects", json=body)
    assert duplicate.status_code == 409
    assert duplicate.get_json()["error"] == "That project ID is taken. Pick a different one."


def test_create_project_lists_missing_fields(client):
    response = client.post("/api/projects", json={"projectId": "proj-3"})
    assert response.status_code == 400
    assert "name" in response.get_json()["error"]


def test_get_unknown_project_returns_404(client):
    response = client.get("/api/projects/does-not-exist")
    assert response.status_code == 404
    assert response.get_json()["error"] == 'No project has the ID "does-not-exist".'


def test_list_projects_returns_summaries_sorted_by_name(client):
    assert client.get("/api/projects").get_json() == []

    for project_id, name in [("p-b", "Zine shoot"), ("p-a", "audio drama")]:
        client.post(
            "/api/projects",
            json={"projectId": project_id, "name": name, "description": "d"},
        )

    response = client.get("/api/projects")
    assert response.status_code == 200
    assert response.get_json() == [
        {"projectId": "p-a", "name": "audio drama", "ownerUserid": "alice", "members": ["alice"]},
        {"projectId": "p-b", "name": "Zine shoot", "ownerUserid": "alice", "members": ["alice"]},
    ]
def test_session_survives_a_refresh_and_signout_ends_it(client):
    assert client.get("/api/auth/me").get_json() == {"userid": "alice"}
    client.post("/api/auth/signout")
    assert client.get("/api/auth/me").get_json() == {"userid": None}


def test_short_passwords_are_rejected(app):
    response = app.test_client().post("/api/auth/signup", json={"userid": "dan", "password": "short"})
    assert response.status_code == 400


def test_signed_out_users_cannot_use_projects_or_kits(app):
    browser = app.test_client()
    assert browser.get("/api/projects/p").status_code == 401
    assert browser.post("/api/hardware/checkout", json={}).status_code == 401


def test_project_owner_comes_from_the_session_not_the_body(client):
    response = client.post(
        "/api/projects",
        json={"projectId": "p-x", "name": "X", "description": "d", "ownerUserid": "mallory"},
    )
    assert response.get_json()["ownerUserid"] == "alice"


def test_signed_out_users_cannot_list_projects(app):
    assert app.test_client().get("/api/projects").status_code == 401


def test_signin_rejects_query_operators(app):
    browser = app.test_client()
    browser.post("/api/auth/signup", json={"userid": "erin", "password": "erin-pass"})
    browser.post("/api/auth/signout")

    response = browser.post(
        "/api/auth/signin", json={"userid": {"$ne": None}, "password": "erin-pass"}
    )
    assert response.status_code == 400
    assert browser.get("/api/auth/me").get_json() == {"userid": None}


def test_create_project_rejects_non_strings_and_slashes(client):
    operator = client.post(
        "/api/projects", json={"projectId": {"$ne": None}, "name": "X", "description": "d"}
    )
    assert operator.status_code == 400
    assert operator.get_json()["error"] == "Missing fields: projectId."

    slash = client.post("/api/projects", json={"projectId": "a/b", "name": "X", "description": "d"})
    assert slash.status_code == 400
