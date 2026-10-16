"""Sign-up / sign-in endpoints (SN1, SR1, SR2).

Error messages match the frontend stubs (creator-eaas/src/api/index.js),
since the UI shows them to users as-is.
"""

from flask import Blueprint, jsonify, request

from extensions import get_db
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _read_credentials():
    data = request.get_json(silent=True) or {}
    return data.get("userid"), data.get("password")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    userid, password = _read_credentials()
    if not userid or not password:
        return jsonify({"error": "Enter a user ID and a password."}), 400

    db = get_db()
    created = User.create(db, userid, password)
    if not created:
        return jsonify({"error": "That user ID is taken. Try another one."}), 409
    return jsonify({"userid": userid}), 201


@auth_bp.route("/signin", methods=["POST"])
def signin():
    userid, password = _read_credentials()
    if not userid or not password:
        return jsonify({"error": "Enter a user ID and a password."}), 400

    db = get_db()
    if User.verify(db, userid, password):
        return jsonify({"userid": userid}), 200
    return jsonify({"error": "User ID or password is incorrect."}), 401
