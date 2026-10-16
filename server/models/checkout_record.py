"""Checkout record model (SR7, SR8: record checkouts and returns).

This is kept separate from Hardware so we have a history of who checked
out what and when -- Hardware itself only tracks live capacity/availability
counts.
"""

import datetime


class CheckoutRecord:
    collection_name = "checkout_records"

    @staticmethod
    def create(db, project_id, set_id, quantity):
        doc = {
            "projectId": project_id,
            "setId": set_id,
            "quantity": quantity,
            "checkedOutAt": datetime.datetime.now(datetime.timezone.utc),
            "checkedInAt": None,
        }
        db[CheckoutRecord.collection_name].insert_one(doc)
        doc.pop("_id", None)
        return doc

    @staticmethod
    def active_for_project(db, project_id, set_id):
        """Checkouts for this project/set that haven't been checked back in."""
        return list(
            db[CheckoutRecord.collection_name].find(
                {"projectId": project_id, "setId": set_id, "checkedInAt": None},
                {"_id": 0},
            )
        )
