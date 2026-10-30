"""Project create/access endpoints (SN1, SR3, SR4)."""

from flask import Blueprint, jsonify, request

from extensions import get_projects_db, get_users_db
from models.project import Project
from models.user import User
from session_auth import current_userid, login_required

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")

REQUIRED_FIELDS = ["projectId", "name", "description"]
NOT_SHARED = "This project isn't shared with you."


def _not_shared():
    return jsonify({"error": NOT_SHARED}), 403


def _load_member_project(project_id):
    """The project, if the signed-in user is on its crew.

    Returns (project, error_response). error_response is None when the
    caller may use the project.
    """
    project = Project.get(get_projects_db(), project_id)
    if not project:
        return None, (jsonify({"error": f'No project has the ID "{project_id}".'}), 404)
    if not Project.has_access(project, current_userid()):
        return None, _not_shared()
    return project, None


def _read_userid():
    """A userid string from the JSON body, or None when it isn't a string.

    A JSON object like {"$ne": null} must not reach Mongo as a query.
    """
    data = request.get_json(silent=True) or {}
    userid = data.get("userid")
    if not isinstance(userid, str):
        return None
    return userid.strip()


@projects_bp.route("", methods=["GET"])
@login_required
def list_projects():
    return jsonify(Project.list_for(get_projects_db(), current_userid())), 200


@projects_bp.route("", methods=["POST"])
@login_required
def create_project():
    data = request.get_json(silent=True) or {}
    # Non-strings count as missing, so a JSON object can't reach Mongo as a
    # query operator.
    missing = [
        field
        for field in REQUIRED_FIELDS
        if not isinstance(data.get(field), str) or not data[field].strip()
    ]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}."}), 400
    # /api/projects/<projectId> can't route an ID with a slash in it.
    if "/" in data["projectId"]:
        return jsonify({"error": "Project IDs can't contain a slash (/)."}), 400

    db = get_projects_db()
    project = Project.create(
        db, data["projectId"], data["name"], data["description"], current_userid()
    )
    if not project:
        return jsonify({"error": "That project ID is taken. Pick a different one."}), 409
    return jsonify(project), 201


@projects_bp.route("/<project_id>", methods=["GET"])
@login_required
def get_project(project_id):
    project, error = _load_member_project(project_id)
    if error:
        return error
    return jsonify(Project.public(project)), 200


@projects_bp.route("/<project_id>/members", methods=["POST"])
@login_required
def share_project(project_id):
    """Add an existing account to this project's crew."""
    project, error = _load_member_project(project_id)
    if error:
        return error

    userid = _read_userid()
    if not userid:
        return jsonify({"error": "Enter a user ID."}), 400

    account = User.find(get_users_db(), userid)
    if not account:
        return jsonify({"error": f'No account has the user ID "{userid}".'}), 404

    # Store the userid as it was created, not whatever case was typed.
    updated = Project.add_member(get_projects_db(), project_id, account["userid"])
    if not updated:
        return jsonify({"error": f'{account["userid"]} is already on this project.'}), 409
    return jsonify(updated), 200


@projects_bp.route("/<project_id>/members/<member_id>", methods=["DELETE"])
@login_required
def unshare_project(project_id, member_id):
    """Take someone off the crew. The owner always stays."""
    project, error = _load_member_project(project_id)
    if error:
        return error
    if member_id == project.get("ownerUserid"):
        return jsonify({"error": "The owner stays on the project."}), 400

    updated = Project.remove_member(get_projects_db(), project_id, member_id)
    if not updated:
        return jsonify({"error": f'{member_id} isn’t on this project.'}), 404
    return jsonify(updated), 200
