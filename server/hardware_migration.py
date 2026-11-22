"""Move hardware data into the hardware database.

Hardware sets and checkout history used to live in the projects database.
They now have a database of their own. A deployment that already has kits
checked out must keep its live counts, or a project could check in kits
the fresh shelf never knew were out (and push "available" past capacity).

So every startup, before the hardware sets are seeded, this copies over
any hardware set or checkout record the hardware database doesn't have
yet. The originals are left where they were; nothing is deleted.

Every write is "insert only if missing" (sets matched by setId, history
by _id), so it never changes data already in the hardware database, and
two server workers starting at the same moment can both run it without
duplicating anything. Once every deployment has started on the new code,
this file can be removed.
"""


def copy_hardware_from_projects_db(projects_db, hardware_db):
    """Copy missing hardware sets and checkout history from the projects
    database into the hardware database. Returns how many documents were
    copied, per collection.
    """
    copied = {"hardware_sets": 0, "checkout_records": 0}
    if projects_db.name == hardware_db.name and projects_db.client is hardware_db.client:
        return copied  # Same database: nothing to move.

    for doc in projects_db["hardware_sets"].find({}, {"_id": 0}):
        if not isinstance(doc.get("setId"), str):
            continue
        result = hardware_db["hardware_sets"].update_one(
            {"setId": doc["setId"]}, {"$setOnInsert": doc}, upsert=True
        )
        if result.upserted_id is not None:
            copied["hardware_sets"] += 1

    for doc in projects_db["checkout_records"].find({}):
        result = hardware_db["checkout_records"].update_one(
            {"_id": doc["_id"]}, {"$setOnInsert": doc}, upsert=True
        )
        if result.upserted_id is not None:
            copied["checkout_records"] += 1
    return copied
