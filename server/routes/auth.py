"""Sign-up / sign-in endpoints (SN1, SR1, SR2).

Error messages match the frontend stubs (creator-eaas/src/api/index.js),
since the UI shows them to users as-is.
"""

from flask import Blueprint, jsonify, request, session

from extensions import get_db
from models.user import User
from session_auth import current_userid

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _read_credentials():
    """The userid and password, or None for any that is missing or not a
    string. A JSON object like {"$ne": null} would otherwise reach Mongo as
    a query operator and match some other user.
    """
    data = request.get_json(silent=True) or {}
    userid, password = data.get("userid"), data.get("password")
    return (
        userid if isinstance(userid, str) else None,
        password if isinstance(password, str) else None,
    )


def _sign_in(userid):
    session.clear()
    session["userid"] = userid
    session.permanent = True  # keep the cookie after the browser closes


@auth_bp.route("/signup", methods=["POST"])
def signup():
    userid, password = _read_credentials()
    if not userid or not password:
        return jsonify({"error": "Enter a user ID and a password."}), 400
    if len(password) < 8:
        return jsonify({"error": "Use a password with at least 8 characters."}), 400

    db = get_db()
    created = User.create(db, userid, password)
    if not created:
        return jsonify({"error": "That user ID is taken. Try another one."}), 409
    _sign_in(userid)
    return jsonify({"userid": userid}), 201


@auth_bp.route("/signin", methods=["POST"])
def signin():
    userid, password = _read_credentials()
    if not userid or not password:
        return jsonify({"error": "Enter a user ID and a password."}), 400

    db = get_db()
    if User.verify(db, userid, password):
        _sign_in(userid)
        return jsonify({"userid": userid}), 200
    return jsonify({"error": "User ID or password is incorrect."}), 401


@auth_bp.route("/me", methods=["GET"])
def me():
    """Who is signed in (null if nobody). The frontend calls this on page load."""
    return jsonify({"userid": current_userid()}), 200


@auth_bp.route("/signout", methods=["POST"])
def signout():
    session.clear()
    return jsonify({"userid": None}), 200
