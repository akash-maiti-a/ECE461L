"""Project model (SR3, SR4: create a new project / access an existing one).

Field names are camelCase to match the frontend's API contract
(creator-eaas/src/api/index.js), so documents can be returned as-is.
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
