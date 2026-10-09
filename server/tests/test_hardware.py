def test_list_hardware_returns_seeded_sets(client):
    response = client.get("/api/hardware")
    assert response.status_code == 200
    set_ids = {hw["set_id"] for hw in response.get_json()}
    assert set_ids == {"HWSet1", "HWSet2"}


def test_checkout_decrements_availability(client):
    before = {hw["set_id"]: hw for hw in client.get("/api/hardware").get_json()}

    response = client.post(
        "/api/hardware/checkout",
        json={"project_id": "proj-1", "set_id": "HWSet1", "quantity": 2},
    )

    assert response.status_code == 200
    after = {hw["set_id"]: hw for hw in response.get_json()}
    assert after["HWSet1"]["available"] == before["HWSet1"]["available"] - 2


def test_checkout_rejects_insufficient_availability(client):
    response = client.post(
        "/api/hardware/checkout",
        json={"project_id": "proj-1", "set_id": "HWSet1", "quantity": 9999},
    )
    assert response.status_code == 409


def test_checkin_restores_availability(client):
    client.post(
        "/api/hardware/checkout",
        json={"project_id": "proj-1", "set_id": "HWSet2", "quantity": 3},
    )
    response = client.post(
        "/api/hardware/checkin",
        json={"project_id": "proj-1", "set_id": "HWSet2", "quantity": 3},
    )

    assert response.status_code == 200
    after = {hw["set_id"]: hw for hw in response.get_json()}
    assert after["HWSet2"]["available"] == after["HWSet2"]["capacity"]


def test_checkin_cannot_exceed_capacity(client):
    response = client.post(
        "/api/hardware/checkin",
        json={"project_id": "proj-1", "set_id": "HWSet1", "quantity": 999},
    )
    assert response.status_code == 200
    after = {hw["set_id"]: hw for hw in response.get_json()}
    assert after["HWSet1"]["available"] == after["HWSet1"]["capacity"]
