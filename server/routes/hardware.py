"""Hardware status, checkout, and check-in endpoints (SN2-SN5, SR5-SR8)."""

from flask import Blueprint, jsonify, request

from extensions import get_db
from models.checkout_record import CheckoutRecord
from models.hardware import Hardware

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
    if (
        not project_id
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

    return project_id, hardware_set, quantity, None


@hardware_bp.route("", methods=["GET"])
def list_hardware():
    """Capacity and availability for every hardware set (SR5)."""
    db = get_db()
    return jsonify(Hardware.list_all(db)), 200


@hardware_bp.route("/checkout", methods=["POST"])
def checkout():
    """Check out a quantity of a hardware set for a project (SR7)."""
    db = get_db()
    project_id, hardware_set, quantity, error = _parse_request(db)
    if error:
        return error

    set_id = hardware_set["setId"]
    if not Hardware.checkout(db, set_id, quantity):
        # Re-read so the message reflects the count at the moment it failed.
        current = Hardware.get(db, set_id)
        message = f"Only {current['available']} {current['name'].lower()} are on the shelf."
        return jsonify({"error": message}), 409

    CheckoutRecord.create(db, project_id, set_id, quantity)
    return jsonify(Hardware.list_all(db)), 200


@hardware_bp.route("/checkin", methods=["POST"])
def checkin():
    """Check in a quantity of a hardware set, freeing it back up (SR8)."""
    db = get_db()
    project_id, hardware_set, quantity, error = _parse_request(db)
    if error:
        return error

    Hardware.checkin(db, hardware_set["setId"], quantity)
    return jsonify(Hardware.list_all(db)), 200
