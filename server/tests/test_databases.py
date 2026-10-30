import extensions


def test_users_projects_and_hardware_live_in_separate_databases(client, make_project):
    make_project("proj-1")
    mongo = extensions._client

    assert mongo["haas_users"]["users"].find_one({"userid": "alice"})
    assert mongo["haas_projects"]["projects"].find_one({"projectId": "proj-1"})
    assert mongo["haas_hardware"]["hardware_sets"].find_one({"setId": "HWSet1"})

    assert "users" not in mongo["haas_projects"].list_collection_names()
    assert "projects" not in mongo["haas_users"].list_collection_names()
    assert "hardware_sets" not in mongo["haas_users"].list_collection_names()
