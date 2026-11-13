"""Project create/access endpoints (SN1, SR3, SR4)."""

from flask import Blueprint, jsonify, request

from extensions import get_projects_db
from models.project import Project
from session_auth import current_userid, login_required

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")

REQUIRED_FIELDS = ["projectId", "name", "description"]
NOT_JOINED = "You haven't joined this project. Enter its project ID under Join a project."


def _not_joined():
    return jsonify({"error": NOT_JOINED}), 403


def _load_project(project_id):
    """The project, or (None, 404 response) if no project has that ID."""
    project = Project.get(get_projects_db(), project_id)
    if not project:
        return None, (jsonify({"error": f'No project has the ID "{project_id}".'}), 404)
    return project, None




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
    """Only people who created or joined the project can open it."""
    project, error = _load_project(project_id)
    if error:
        return error
    if not Project.has_access(project, current_userid()):
        return _not_joined()
    return jsonify(Project.public(project)), 200


@projects_bp.route("/<project_id>/join", methods=["POST"])
@login_required
def join_project(project_id):
    """Join a project by typing its exact ID (SR4).

    Knowing the ID is all it takes. Joining a project you're already on
    just opens it again.
    """
    project, error = _load_project(project_id)
    if error:
        return error
    return jsonify(Project.add_member(get_projects_db(), project, current_userid())), 200
