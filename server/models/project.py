"""Project model (SR3, SR4: create a new project / access an existing one).

Field names are camelCase to match the frontend's API contract
(creator-eaas/src/api/index.js), so documents can be returned as-is.

Each project also keeps a running tally of the kits it has out, e.g.
{"checkedOut": {"HWSet1": 3}}. That tally is what stops a project from
checking in more kits than it borrowed (SR8).

`members` is the crew: userids who can open the project and check kits
in and out. The owner is always first. Anyone signed in joins a project
by typing its exact projectId; there are no invites. Projects created
before `members` existed belong to just their owner until someone joins.
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
            "members": [owner_userid],
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
    def member_ids(doc):
        """Userids who can use this project, owner first.

        A missing or malformed `members` list means just the owner, which
        is how projects stored before sharing still behave.
        """
        owner = doc.get("ownerUserid")
        members = []
        if isinstance(owner, str) and owner:
            members.append(owner)
        raw = doc.get("members")
        if isinstance(raw, list):
            for userid in raw:
                if isinstance(userid, str) and userid and userid not in members:
                    members.append(userid)
        return members

    @staticmethod
    def has_access(doc, userid):
        """Whether this user is on the crew, so may change the project."""
        return userid in Project.member_ids(doc)

    @staticmethod
    def public(doc, summary=False):
        """The document the API returns. `summary` is the dropdown shape."""
        members = Project.member_ids(doc)
        if summary:
            return {
                "projectId": doc.get("projectId"),
                "name": doc.get("name", ""),
                "ownerUserid": doc.get("ownerUserid"),
                "members": members,
            }
        out = {key: value for key, value in doc.items() if key != "_id"}
        out["members"] = members
        out.pop("open", None)
        out.setdefault("checkedOut", {})
        return out

    @staticmethod
    def list_for(db, userid):
        """The projects this user created or joined, sorted by name.

        Feeds the frontend's project dropdowns, so it leaves out
        descriptions and checkout tallies.
        """
        cursor = db[Project.collection_name].find(
            {"$or": [{"ownerUserid": userid}, {"members": userid}]},
            {"_id": 0, "projectId": 1, "name": 1, "ownerUserid": 1, "members": 1},
        )
        # str() so one odd document (say, added by hand in Atlas) can't break sorting.
        projects = sorted(
            cursor, key=lambda p: (str(p.get("name", "")).lower(), str(p.get("projectId")))
        )
        return [Project.public(project, summary=True) for project in projects]

    @staticmethod
    def add_member(db, project, userid):
        """Put userid on the project's crew and return the updated project.

        Joining twice is harmless: someone already on the crew just gets
        the project back. $addToSet means two people joining at once can't
        overwrite each other. The owner goes in first so projects stored
        before `members` existed keep their owner at the front.
        """
        owner = project.get("ownerUserid")
        to_add = [owner, userid] if isinstance(owner, str) and owner else [userid]
        db[Project.collection_name].update_one(
            {"projectId": project["projectId"]},
            {"$addToSet": {"members": {"$each": to_add}}},
        )
        return Project.public(Project.get(db, project["projectId"]))

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
