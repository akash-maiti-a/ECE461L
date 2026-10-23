import extensions
from models.checkout_record import CheckoutRecord
from models.hardware import Hardware


def hardware_by_id(response):
    return {hw["setId"]: hw for hw in response.get_json()}


def checkout(client, project_id, set_id, quantity):
    return client.post(
        "/api/hardware/checkout",
        json={"projectId": project_id, "setId": set_id, "quantity": quantity},
    )


def checkin(client, project_id, set_id, quantity):
    return client.post(
        "/api/hardware/checkin",
        json={"projectId": project_id, "setId": set_id, "quantity": quantity},
    )


def checked_out(client, project_id, set_id):
    project = client.get(f"/api/projects/{project_id}").get_json()
    return project["checkedOut"].get(set_id, 0)


# ---------- Listing and seeding ----------


def test_list_hardware_returns_seeded_sets(client):
    response = client.get("/api/hardware")
    assert response.status_code == 200
    assert set(hardware_by_id(response)) == {"HWSet1", "HWSet2"}


def test_seeded_sets_match_the_landing_page(client):
    hardware = hardware_by_id(client.get("/api/hardware"))

    assert hardware["HWSet1"]["name"] == "Camera kits"
    assert hardware["HWSet1"]["capacity"] == 10
    assert hardware["HWSet2"]["name"] == "Audio and lighting kits"
    assert hardware["HWSet2"]["capacity"] == 8
    for hw in hardware.values():
        assert hw["available"] == hw["capacity"]
        assert len(hw["contents"]) > 0


def test_reseeding_keeps_live_availability(client, make_project):
    project_id = make_project()
    checkout(client, project_id, "HWSet1", 4)

    # Simulates the server restarting, which runs seed() again.
    Hardware.seed(extensions.get_db())

    hardware = hardware_by_id(client.get("/api/hardware"))
    assert hardware["HWSet1"]["available"] == 6


# ---------- Checkout ----------


def test_checkout_updates_shelf_and_project_tally(client, make_project):
    project_id = make_project()

    response = checkout(client, project_id, "HWSet1", 2)

    assert response.status_code == 200
    assert hardware_by_id(response)["HWSet1"]["available"] == 8
    assert checked_out(client, project_id, "HWSet1") == 2


def test_checkout_rejects_insufficient_availability(client, make_project):
    project_id = make_project()

    response = checkout(client, project_id, "HWSet1", 9999)

    assert response.status_code == 409
    assert response.get_json()["error"] == "Only 10 camera kits are on the shelf."
    assert checked_out(client, project_id, "HWSet1") == 0


def test_checkout_unknown_set_returns_404(client, make_project):
    response = checkout(client, make_project(), "HWSet9", 1)
    assert response.status_code == 404
    assert response.get_json()["error"] == 'Unknown hardware set "HWSet9".'


def test_checkout_unknown_project_returns_404(client):
    response = checkout(client, "no-such-project", "HWSet1", 1)

    assert response.status_code == 404
    assert response.get_json()["error"] == 'No project has the ID "no-such-project".'
    assert hardware_by_id(client.get("/api/hardware"))["HWSet1"]["available"] == 10


def test_checkout_rejects_non_integer_quantities(client, make_project):
    project_id = make_project()
    for bad_quantity in [0, -1, 1.5, "2", True, None]:
        response = checkout(client, project_id, "HWSet1", bad_quantity)
        assert response.status_code == 400, bad_quantity


# ---------- Check-in ----------


def test_checkin_restores_shelf_and_project_tally(client, make_project):
    project_id = make_project()
    checkout(client, project_id, "HWSet2", 3)

    response = checkin(client, project_id, "HWSet2", 3)

    assert response.status_code == 200
    assert hardware_by_id(response)["HWSet2"]["available"] == 8
    assert checked_out(client, project_id, "HWSet2") == 0


def test_partial_checkin(client, make_project):
    project_id = make_project()
    checkout(client, project_id, "HWSet1", 5)

    response = checkin(client, project_id, "HWSet1", 2)

    assert response.status_code == 200
    assert hardware_by_id(response)["HWSet1"]["available"] == 7
    assert checked_out(client, project_id, "HWSet1") == 3


def test_cannot_check_in_more_than_borrowed(client, make_project):
    project_id = make_project()
    checkout(client, project_id, "HWSet1", 2)

    response = checkin(client, project_id, "HWSet1", 3)

    assert response.status_code == 409
    assert response.get_json()["error"] == (
        "This project has 2 camera kits checked out, so it can't check in 3."
    )
    # Nothing changed.
    assert hardware_by_id(client.get("/api/hardware"))["HWSet1"]["available"] == 8
    assert checked_out(client, project_id, "HWSet1") == 2


def test_cannot_check_in_another_projects_kits(client, make_project):
    borrower = make_project("borrower")
    other = make_project("other")
    checkout(client, borrower, "HWSet1", 4)

    response = checkin(client, other, "HWSet1", 4)

    assert response.status_code == 409
    assert hardware_by_id(client.get("/api/hardware"))["HWSet1"]["available"] == 6
    assert checked_out(client, borrower, "HWSet1") == 4


# ---------- History ----------


def test_checkouts_and_checkins_are_logged(client, make_project):
    project_id = make_project()
    checkout(client, project_id, "HWSet1", 2)
    checkin(client, project_id, "HWSet1", 1)
    checkin(client, project_id, "HWSet1", 5)  # rejected, so not logged

    history = CheckoutRecord.for_project(extensions.get_db(), project_id)

    assert [(h["action"], h["setId"], h["quantity"]) for h in history] == [
        ("checkout", "HWSet1", 2),
        ("checkin", "HWSet1", 1),
    ]


def test_checkout_rejects_query_operators_as_ids(client, make_project):
    make_project("proj-op")
    response = checkout(client, {"$ne": None}, "HWSet1", 1)
    assert response.status_code == 400
    assert checked_out(client, "proj-op", "HWSet1") == 0
