"""Hardware set model (SR5: capacity/availability for HWSet1 & HWSet2).

HWSet1 = camera kits, HWSet2 = audio and lighting kits (see docs/requirements.md).
The two sets are seeded on startup so the app never shows hard-coded
numbers on the frontend -- they come from the database from the start.
"""


class Hardware:
    collection_name = "hardware_sets"

    DEFAULT_SETS = [
        {"setId": "HWSet1", "name": "Camera Kits", "capacity": 10, "available": 10},
        {"setId": "HWSet2", "name": "Audio and Lighting Kits", "capacity": 10, "available": 10},
    ]

    @staticmethod
    def seed(db):
        """Insert the default hardware sets if they don't already exist.
        Safe to call on every app startup -- $setOnInsert means existing
        documents (and their current `available` count) are left alone.
        """
        collection = db[Hardware.collection_name]
        for hw in Hardware.DEFAULT_SETS:
            collection.update_one(
                {"setId": hw["setId"]}, {"$setOnInsert": hw}, upsert=True
            )

    @staticmethod
    def list_all(db):
        return list(db[Hardware.collection_name].find({}, {"_id": 0}))

    @staticmethod
    def get(db, set_id):
        """Fetch one hardware set by its setId, or None if it doesn't exist."""
        return db[Hardware.collection_name].find_one({"setId": set_id}, {"_id": 0})

    @staticmethod
    def checkout(db, set_id, quantity):
        """Atomically decrement `available` by quantity, but only if
        enough units are available. Returns True on success, False if
        there wasn't enough availability (or set_id doesn't exist).

        The filter {"available": {"$gte": quantity}} combined with the
        update happening in one call is what makes this safe against two
        requests racing each other -- Mongo won't apply the update unless
        the document still matches the filter at that instant.
        """
        result = db[Hardware.collection_name].update_one(
            {"setId": set_id, "available": {"$gte": quantity}},
            {"$inc": {"available": -quantity}},
        )
        return result.modified_count == 1

    @staticmethod
    def checkin(db, set_id, quantity):
        """Increment `available` by quantity, capped at capacity so a
        bad check-in request can't push availability above the total
        the service owns. Returns True if the set exists.
        """
        hw = db[Hardware.collection_name].find_one({"setId": set_id})
        if not hw:
            return False
        new_available = min(hw["capacity"], hw["available"] + quantity)
        db[Hardware.collection_name].update_one(
            {"setId": set_id}, {"$set": {"available": new_available}}
        )
        return True
