"""Project create/access endpoints (SN1, SR3, SR4)."""

from flask import Blueprint, jsonify, request

from extensions import get_db
from models.project import Project
from session_auth import current_userid, login_required

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")

REQUIRED_FIELDS = ["projectId", "name", "description"]


@projects_bp.route("", methods=["GET"])
def list_projects():
    return jsonify(Project.list_all(get_db())), 200


@projects_bp.route("", methods=["POST"])
@login_required
def create_project():
    data = request.get_json(silent=True) or {}
    missing = [field for field in REQUIRED_FIELDS if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}."}), 400

    db = get_db()
    project = Project.create(
        db, data["projectId"], data["name"], data["description"], current_userid()
    )
    if not project:
        return jsonify({"error": "That project ID is taken. Pick a different one."}), 409
    return jsonify(project), 201


@projects_bp.route("/<project_id>", methods=["GET"])
@login_required
def get_project(project_id):
    db = get_db()
    project = Project.get(db, project_id)
    if not project:
        return jsonify({"error": f'No project has the ID "{project_id}".'}), 404
    return jsonify(project), 200
