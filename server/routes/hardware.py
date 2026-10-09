"""Hardware status, checkout, and check-in endpoints (SN2-SN5, SR5-SR8)."""

from flask import Blueprint, jsonify, request

from extensions import get_db
from models.checkout_record import CheckoutRecord
from models.hardware import Hardware

hardware_bp = Blueprint("hardware", __name__, url_prefix="/api/hardware")

VALID_SET_IDS = {"HWSet1", "HWSet2"}


def _parse_checkout_request(data):
    """Shared validation for the checkout and checkin bodies. Returns
    (project_id, set_id, quantity, error_response). error_response is
    None when the input is valid.
    """
    project_id = data.get("project_id")
    set_id = data.get("set_id")
    quantity = data.get("quantity")
    if (
        not project_id
        or set_id not in VALID_SET_IDS
        or not isinstance(quantity, int)
        or quantity <= 0
    ):
        error = jsonify(
            {
                "error": "project_id, valid set_id (HWSet1/HWSet2), and a "
                "positive integer quantity are required"
            }
        )
        return None, None, None, (error, 400)
    return project_id, set_id, quantity, None


@hardware_bp.route("", methods=["GET"])
def list_hardware():
    """Capacity and availability for both hardware sets (SR5)."""
    db = get_db()
    return jsonify(Hardware.list_all(db)), 200


@hardware_bp.route("/checkout", methods=["POST"])
def checkout():
    """Check out a quantity of a hardware set for a project (SR7)."""
    data = request.get_json(silent=True) or {}
    project_id, set_id, quantity, error = _parse_checkout_request(data)
    if error:
        return error

    db = get_db()
    success = Hardware.checkout(db, set_id, quantity)
    if not success:
        return jsonify({"error": "not enough availability"}), 409

    CheckoutRecord.create(db, project_id, set_id, quantity)
    return jsonify(Hardware.list_all(db)), 200


@hardware_bp.route("/checkin", methods=["POST"])
def checkin():
    """Check in a quantity of a hardware set, freeing it back up (SR8)."""
    data = request.get_json(silent=True) or {}
    project_id, set_id, quantity, error = _parse_checkout_request(data)
    if error:
        return error

    db = get_db()
    success = Hardware.checkin(db, set_id, quantity)
    if not success:
        return jsonify({"error": "unknown set_id"}), 404
    return jsonify(Hardware.list_all(db)), 200
