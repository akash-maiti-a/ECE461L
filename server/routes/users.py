"""Look up accounts so the share field can suggest user IDs that exist."""

from flask import Blueprint, jsonify, request

from extensions import get_users_db
from models.user import User
from session_auth import login_required

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["GET"])
@login_required
def search_users():
    """GET /api/users?q=al  ->  [{userid}, ...] for accounts starting with q.

    A blank query returns nobody. Matches are plain text, so a "." in the
    query doesn't become a wildcard.
    """
    query = request.args.get("q", "")
    if not isinstance(query, str):
        query = ""
    query = query.strip()
    if len(query) > 64:
        return jsonify({"error": "That user ID is too long."}), 400
    return jsonify(User.search(get_users_db(), query)), 200
