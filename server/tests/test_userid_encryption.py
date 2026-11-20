"""User IDs are encrypted in the users database (SR3)."""

import json

from werkzeug.security import generate_password_hash

import extensions
from userid_crypto import decrypt_userid, userid_hash


def users():
    return extensions.get_users_db()["users"]


def test_the_database_never_holds_the_plain_user_id(app, client):
    stored = users().find_one({})
    assert set(stored) == {"_id", "userid_hash", "userid_encrypted", "password_hash"}
    raw = json.dumps({k: v for k, v in stored.items() if k != "_id"})
    assert "alice" not in raw
    assert "alice-pass" not in raw


def test_the_encrypted_user_id_decrypts_with_the_key(app, client):
    stored = users().find_one({})
    with app.app_context():
        assert decrypt_userid(stored["userid_encrypted"]) == "alice"
        assert stored["userid_hash"] == userid_hash("alice")


def test_encrypting_the_same_id_twice_gives_different_ciphertext(app):
    first = app.test_client().post("/api/auth/signup", json={"userid": "bob", "password": "bob-pass1"})
    second = app.test_client().post("/api/auth/signup", json={"userid": "carol", "password": "carol-pass"})
    assert first.status_code == second.status_code == 201
    ciphertexts = {doc["userid_encrypted"] for doc in users().find({})}
    assert len(ciphertexts) == 2


def test_sign_in_and_duplicate_check_still_work(app, client):
    taken = app.test_client().post("/api/auth/signup", json={"userid": "alice", "password": "x-pass-123"})
    assert taken.status_code == 409
    good = app.test_client().post("/api/auth/signin", json={"userid": "alice", "password": "alice-pass"})
    assert good.status_code == 200
    assert good.get_json() == {"userid": "alice"}
    wrong_case = app.test_client().post("/api/auth/signin", json={"userid": "Alice", "password": "alice-pass"})
    assert wrong_case.status_code == 401


def test_a_different_key_cannot_find_the_account(app, client):
    app.config["USERID_ENCRYPTION_KEY"] = "some-other-key"
    response = app.test_client().post("/api/auth/signin", json={"userid": "alice", "password": "alice-pass"})
    assert response.status_code == 401


def test_accounts_stored_before_encryption_sign_in_and_get_converted(app):
    users().insert_one({"userid": "dana", "password_hash": generate_password_hash("dana-pass")})

    assert app.test_client().post(
        "/api/auth/signup", json={"userid": "dana", "password": "new-pass-1"}
    ).status_code == 409
    assert app.test_client().post(
        "/api/auth/signin", json={"userid": "dana", "password": "wrong-pass"}
    ).status_code == 401
    assert users().find_one({"userid": "dana"}) is not None  # wrong password changes nothing

    good = app.test_client().post("/api/auth/signin", json={"userid": "dana", "password": "dana-pass"})
    assert good.status_code == 200
    stored = users().find_one({})
    assert "userid" not in stored
    with app.app_context():
        assert decrypt_userid(stored["userid_encrypted"]) == "dana"
    again = app.test_client().post("/api/auth/signin", json={"userid": "dana", "password": "dana-pass"})
    assert again.status_code == 200
