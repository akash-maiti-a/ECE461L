"""Shared, app-wide resources (currently just the Mongo connection).

Routes and models call get_db() to reach the database rather than each
creating their own connection. This also gives tests a single seam
(extensions.MongoClient) to swap in an in-memory database.
"""

from pymongo import MongoClient

_client = None
_db = None


def init_db(app):
    """Connect to Mongo using the app's configured URI and store the
    database handle for the rest of the app to use. Called once, from
    create_app().
    """
    global _client, _db
    mongo_uri = app.config["MONGO_URI"]
    _client = MongoClient(mongo_uri)
    _db = _client.get_default_database()
    return _db


def get_db():
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db(app) first.")
    return _db
