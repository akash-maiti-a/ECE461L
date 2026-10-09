"""Project create/access endpoints (SN1, SR3, SR4)."""

from flask import Blueprint, jsonify, request

from extensions import get_db
from models.project import Project

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")


@projects_bp.route("", methods=["POST"])
def create_project():
    data = request.get_json(silent=True) or {}
    required_fields = ["project_id", "name", "description", "owner_userid"]
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify({"error": f"missing fields: {', '.join(missing)}"}), 400

    db = get_db()
    project = Project.create(
        db, data["project_id"], data["name"], data["description"], data["owner_userid"]
    )
    if not project:
        return jsonify({"error": "project_id already exists"}), 409
    return jsonify(project), 201


@projects_bp.route("/<project_id>", methods=["GET"])
def get_project(project_id):
    db = get_db()
    project = Project.get(db, project_id)
    if not project:
        return jsonify({"error": "project not found"}), 404
    return jsonify(project), 200
