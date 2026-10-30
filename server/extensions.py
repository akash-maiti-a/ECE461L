"""Shared, app-wide resources (currently just the Mongo connection).

Routes and models call get_db() to reach the database rather than each
creating their own connection. This also gives tests a single seam
(extensions.MongoClient) to swap in an in-memory database.

Users, projects, and hardware each live in their own MongoDB database.
get_db() returns a router, so models still write db["users"] and land in
the right database without knowing about the split.
"""

from pymongo import MongoClient

# Collection name -> database it lives in. Checkout history sits with the
# hardware sets it describes.
DATABASES = {
    "users": "haas_users",
    "projects": "haas_projects",
    "hardware_sets": "haas_hardware",
    "checkout_records": "haas_hardware",
}

_client = None
_db = None


class DatabaseRouter:
    """Looks like a single pymongo Database for db[collection_name], but
    sends each collection to the database named in DATABASES.
    """

    def __init__(self, client):
        self.client = client

    def __getitem__(self, collection_name):
        if collection_name not in DATABASES:
            raise KeyError(f'No database configured for collection "{collection_name}".')
        return self.client[DATABASES[collection_name]][collection_name]


def init_db(app):
    """Connect to Mongo using the app's configured URI and store the
    database router for the rest of the app to use. Called once, from
    create_app().
    """
    global _client, _db
    if app.config.get("USE_MOCK_DB"):
        import mongomock

        _client = mongomock.MongoClient()
    else:
        _client = MongoClient(app.config["MONGO_URI"])
    _db = DatabaseRouter(_client)
    return _db


def get_db():
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db(app) first.")
    return _db
