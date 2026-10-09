"""Sign-up / sign-in endpoints (SN1, SR1, SR2)."""

from flask import Blueprint, jsonify, request

from extensions import get_db
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    userid = data.get("userid")
    password = data.get("password")
    if not userid or not password:
        return jsonify({"error": "userid and password are required"}), 400

    db = get_db()
    created = User.create(db, userid, password)
    if not created:
        return jsonify({"error": "userid already exists"}), 409
    return jsonify({"userid": userid}), 201


@auth_bp.route("/signin", methods=["POST"])
def signin():
    data = request.get_json(silent=True) or {}
    userid = data.get("userid")
    password = data.get("password")
    if not userid or not password:
        return jsonify({"error": "userid and password are required"}), 400

    db = get_db()
    if User.verify(db, userid, password):
        return jsonify({"userid": userid}), 200
    return jsonify({"error": "invalid credentials"}), 401
