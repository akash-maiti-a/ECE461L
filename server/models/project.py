"""Project model (SR3, SR4: create a new project / access an existing one)."""


class Project:
    collection_name = "projects"

    @staticmethod
    def create(db, project_id, name, description, owner_userid):
        """Create a new project. Returns the stored document, or None if
        project_id is already taken.
        """
        collection = db[Project.collection_name]
        if collection.find_one({"project_id": project_id}):
            return None
        doc = {
            "project_id": project_id,
            "name": name,
            "description": description,
            "owner_userid": owner_userid,
        }
        collection.insert_one(doc)
        # Mongo adds an internal _id field on insert; we leave it out of
        # API responses since the client only needs project_id.
        doc.pop("_id", None)
        return doc

    @staticmethod
    def get(db, project_id):
        """Fetch a project by its project_id, or None if it doesn't exist."""
        return db[Project.collection_name].find_one({"project_id": project_id}, {"_id": 0})
