def test_signup_then_duplicate_is_rejected(client):
    first = client.post("/api/auth/signup", json={"userid": "alice", "password": "secret123"})
    assert first.status_code == 201

    second = client.post("/api/auth/signup", json={"userid": "alice", "password": "other"})
    assert second.status_code == 409


def test_signin_requires_correct_password(client):
    client.post("/api/auth/signup", json={"userid": "bob", "password": "correct-horse"})

    good = client.post("/api/auth/signin", json={"userid": "bob", "password": "correct-horse"})
    assert good.status_code == 200

    bad = client.post("/api/auth/signin", json={"userid": "bob", "password": "wrong"})
    assert bad.status_code == 401


def test_create_and_get_project(client):
    create = client.post(
        "/api/projects",
        json={
            "project_id": "proj-1",
            "name": "Demo Project",
            "description": "A test project",
            "owner_userid": "alice",
        },
    )
    assert create.status_code == 201

    get = client.get("/api/projects/proj-1")
    assert get.status_code == 200
    assert get.get_json()["name"] == "Demo Project"


def test_create_project_duplicate_id_rejected(client):
    body = {
        "project_id": "proj-2",
        "name": "First",
        "description": "desc",
        "owner_userid": "alice",
    }
    assert client.post("/api/projects", json=body).status_code == 201
    assert client.post("/api/projects", json=body).status_code == 409


def test_get_unknown_project_returns_404(client):
    response = client.get("/api/projects/does-not-exist")
    assert response.status_code == 404
