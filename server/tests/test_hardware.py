def hardware_by_id(response):
    return {hw["setId"]: hw for hw in response.get_json()}


def test_list_hardware_returns_seeded_sets(client):
    response = client.get("/api/hardware")
    assert response.status_code == 200
    assert set(hardware_by_id(response)) == {"HWSet1", "HWSet2"}


def test_checkout_decrements_availability(client):
    before = hardware_by_id(client.get("/api/hardware"))

    response = client.post(
        "/api/hardware/checkout",
        json={"projectId": "proj-1", "setId": "HWSet1", "quantity": 2},
    )

    assert response.status_code == 200
    after = hardware_by_id(response)
    assert after["HWSet1"]["available"] == before["HWSet1"]["available"] - 2


def test_checkout_rejects_insufficient_availability(client):
    response = client.post(
        "/api/hardware/checkout",
        json={"projectId": "proj-1", "setId": "HWSet1", "quantity": 9999},
    )
    assert response.status_code == 409
    assert response.get_json()["error"].endswith("are on the shelf.")


def test_checkout_unknown_set_returns_404(client):
    response = client.post(
        "/api/hardware/checkout",
        json={"projectId": "proj-1", "setId": "HWSet9", "quantity": 1},
    )
    assert response.status_code == 404
    assert response.get_json()["error"] == 'Unknown hardware set "HWSet9".'


def test_checkout_rejects_non_integer_quantities(client):
    for bad_quantity in [0, -1, 1.5, "2", True, None]:
        response = client.post(
            "/api/hardware/checkout",
            json={"projectId": "proj-1", "setId": "HWSet1", "quantity": bad_quantity},
        )
        assert response.status_code == 400, bad_quantity


def test_checkin_restores_availability(client):
    client.post(
        "/api/hardware/checkout",
        json={"projectId": "proj-1", "setId": "HWSet2", "quantity": 3},
    )
    response = client.post(
        "/api/hardware/checkin",
        json={"projectId": "proj-1", "setId": "HWSet2", "quantity": 3},
    )

    assert response.status_code == 200
    after = hardware_by_id(response)
    assert after["HWSet2"]["available"] == after["HWSet2"]["capacity"]


def test_checkin_cannot_exceed_capacity(client):
    response = client.post(
        "/api/hardware/checkin",
        json={"projectId": "proj-1", "setId": "HWSet1", "quantity": 999},
    )
    assert response.status_code == 200
    after = hardware_by_id(response)
    assert after["HWSet1"]["available"] == after["HWSet1"]["capacity"]
