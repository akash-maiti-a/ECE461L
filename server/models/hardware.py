"""Hardware set model (SR5: capacity/availability for HWSet1 & HWSet2).

HWSet1 = camera kits, HWSet2 = audio and lighting kits (see docs/requirements.md).
The two sets are seeded on startup so the app never shows hard-coded
numbers on the frontend -- they come from the database from the start.
"""


class Hardware:
    collection_name = "hardware_sets"

    # Same names, capacities, and contents the landing page showed from its
    # stubs. The contents are still placeholders for the team to replace
    # with the real gear list.
    DEFAULT_SETS = [
        {
            "setId": "HWSet1",
            "name": "Camera kits",
            "capacity": 10,
            "contents": [
                "Mirrorless camera body",
                "24–70mm zoom lens",
                "Three batteries and a charger",
                "Two 128 GB SD cards",
                "Fluid-head tripod",
            ],
        },
        {
            "setId": "HWSet2",
            "name": "Audio and lighting kits",
            "capacity": 8,
            "contents": [
                "Shotgun mic with boom pole",
                "Field recorder",
                "Wired lav mic",
                "Two LED panels with stands",
                "Sandbags and gaffer tape",
            ],
        },
    ]

    @staticmethod
    def seed(db):
        """Make sure every default hardware set exists. Safe to call on
        every app startup.

        - name and contents are always refreshed ($set), so editing the
          kit list above updates an existing database on the next restart.
        - capacity and available are only written when the set is first
          created ($setOnInsert), so a restart never wipes out the live
          count of kits that are checked out.
        """
        collection = db[Hardware.collection_name]
        for hw in Hardware.DEFAULT_SETS:
            collection.update_one(
                {"setId": hw["setId"]},
                {
                    "$set": {"name": hw["name"], "contents": hw["contents"]},
                    "$setOnInsert": {"capacity": hw["capacity"], "available": hw["capacity"]},
                },
                upsert=True,
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
        """Put `quantity` kits back on the shelf.

        Callers must first confirm the project actually has that many out
        (Project.remove_checked_out). That check is what keeps `available`
        from ever exceeding `capacity`, so no cap is needed here.
        """
        db[Hardware.collection_name].update_one(
            {"setId": set_id}, {"$inc": {"available": quantity}}
        )
