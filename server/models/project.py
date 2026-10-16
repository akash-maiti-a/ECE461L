"""Project model (SR3, SR4: create a new project / access an existing one).

Field names are camelCase to match the frontend's API contract
(creator-eaas/src/api/index.js), so documents can be returned as-is.

Each project also keeps a running tally of the kits it has out, e.g.
{"checkedOut": {"HWSet1": 3}}. That tally is what stops a project from
checking in more kits than it borrowed (SR8).
"""


class Project:
    collection_name = "projects"

    @staticmethod
    def create(db, project_id, name, description, owner_userid):
        """Create a new project. Returns the stored document, or None if
        project_id is already taken.
        """
        collection = db[Project.collection_name]
        if collection.find_one({"projectId": project_id}):
            return None
        doc = {
            "projectId": project_id,
            "name": name,
            "description": description,
            "ownerUserid": owner_userid,
            "checkedOut": {},
        }
        collection.insert_one(doc)
        # Mongo adds an internal _id field on insert; we leave it out of
        # API responses since the client only needs projectId.
        doc.pop("_id", None)
        return doc

    @staticmethod
    def get(db, project_id):
        """Fetch a project by its projectId, or None if it doesn't exist."""
        return db[Project.collection_name].find_one({"projectId": project_id}, {"_id": 0})

    @staticmethod
    def add_checked_out(db, project_id, set_id, quantity):
        """Record that the project took `quantity` more kits from a set."""
        db[Project.collection_name].update_one(
            {"projectId": project_id},
            {"$inc": {f"checkedOut.{set_id}": quantity}},
        )

    @staticmethod
    def remove_checked_out(db, project_id, set_id, quantity):
        """Lower the project's tally for a set, but only if it has at least
        `quantity` kits out. Returns True on success.

        Like Hardware.checkout, the check and the update happen in one
        database call, so two check-ins at once can't both succeed and
        drive the tally negative. A missing tally counts as zero, which
        never matches the $gte filter.
        """
        field = f"checkedOut.{set_id}"
        result = db[Project.collection_name].update_one(
            {"projectId": project_id, field: {"$gte": quantity}},
            {"$inc": {field: -quantity}},
        )
        return result.modified_count == 1
