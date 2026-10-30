"""Hardware status, checkout, and check-in endpoints (SN2-SN5, SR5-SR8)."""

from flask import Blueprint, jsonify, request

from extensions import get_db
from models.checkout_record import CheckoutRecord
from models.hardware import Hardware
from models.project import Project
from routes.projects import NOT_SHARED
from session_auth import current_userid, login_required

hardware_bp = Blueprint("hardware", __name__, url_prefix="/api/hardware")


def _parse_request(db):
    """Shared validation for the checkout and checkin bodies.

    Returns (project_id, hardware_set, quantity, error_response), where
    error_response is None when the input is valid. Set IDs are checked
    against the database rather than a hard-coded list, so adding HWSet3
    later only means adding a document (SN6).
    """
    data = request.get_json(silent=True) or {}
    project_id = data.get("projectId")
    set_id = data.get("setId")
    quantity = data.get("quantity")

    # bool is a subclass of int in Python, so rule it out explicitly.
    # IDs must be strings: a JSON object like {"$ne": null} would reach Mongo
    # as a query operator and match some other project or set.
    if (
        not isinstance(project_id, str)
        or not project_id
        or not isinstance(set_id, str)
        or not set_id
        or not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        error = jsonify(
            {"error": "Send a projectId, a setId, and a whole-number quantity greater than 0."}
        )
        return None, None, None, (error, 400)

    hardware_set = Hardware.get(db, set_id)
    if not hardware_set:
        return None, None, None, (jsonify({"error": f'Unknown hardware set "{set_id}".'}), 404)

    project = Project.get(db, project_id)
    if not project:
        return None, None, None, (jsonify({"error": f'No project has the ID "{project_id}".'}), 404)
    if not Project.has_access(project, current_userid()):
        return None, None, None, (jsonify({"error": NOT_SHARED}), 403)

    return project_id, hardware_set, quantity, None


@hardware_bp.route("", methods=["GET"])
def list_hardware():
    """Capacity and availability for every hardware set (SR5)."""
    db = get_db()
    return jsonify(Hardware.list_all(db)), 200


@hardware_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    """Check out a quantity of a hardware set for a project (SR7)."""
    db = get_db()
    project_id, hardware_set, quantity, error = _parse_request(db)
    if error:
        return error

    set_id = hardware_set["setId"]
    # Take kits off the shelf first. If that fails, nothing else changes.
    if not Hardware.checkout(db, set_id, quantity):
        # Re-read so the message reflects the count at the moment it failed.
        current = Hardware.get(db, set_id)
        message = f"Only {current['available']} {current['name'].lower()} are on the shelf."
        return jsonify({"error": message}), 409

    Project.add_checked_out(db, project_id, set_id, quantity)
    CheckoutRecord.log(db, project_id, set_id, quantity, "checkout")
    return jsonify(Hardware.list_all(db)), 200


@hardware_bp.route("/checkin", methods=["POST"])
@login_required
def checkin():
    """Check in a quantity of a hardware set, freeing it back up (SR8)."""
    db = get_db()
    project_id, hardware_set, quantity, error = _parse_request(db)
    if error:
        return error

    set_id = hardware_set["setId"]
    # Lower the project's tally first. If the project doesn't have that
    # many out, nothing else changes and the shelf count stays correct.
    if not Project.remove_checked_out(db, project_id, set_id, quantity):
        has_out = Project.get(db, project_id).get("checkedOut", {}).get(set_id, 0)
        message = (
            f"This project has {has_out} {hardware_set['name'].lower()} checked out, "
            f"so it can't check in {quantity}."
        )
        return jsonify({"error": message}), 409

    Hardware.checkin(db, set_id, quantity)
    CheckoutRecord.log(db, project_id, set_id, quantity, "checkin")
    return jsonify(Hardware.list_all(db)), 200
