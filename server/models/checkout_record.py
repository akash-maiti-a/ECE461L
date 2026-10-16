"""Checkout history (SR7, SR8: record checkouts and returns).

Every checkout and check-in adds one entry here. Hardware holds the live
shelf counts and Project holds each project's live tally; this collection
is the history of how they got there, for auditing and for any future
"activity" view in the UI.
"""

import datetime


class CheckoutRecord:
    collection_name = "checkout_records"

    @staticmethod
    def log(db, project_id, set_id, quantity, action):
        """Append one history entry. `action` is "checkout" or "checkin"."""
        db[CheckoutRecord.collection_name].insert_one(
            {
                "projectId": project_id,
                "setId": set_id,
                "quantity": quantity,
                "action": action,
                "at": datetime.datetime.now(datetime.timezone.utc),
            }
        )

    @staticmethod
    def for_project(db, project_id):
        """All history entries for a project, oldest first."""
        return list(
            db[CheckoutRecord.collection_name]
            .find({"projectId": project_id}, {"_id": 0})
            .sort("at", 1)
        )
