"""Shared database connections.

Accounts live in one database. Projects, hardware sets, and checkout
history live in another. The two can sit on the same MongoDB cluster or
on two different clusters, depending on the URIs in the config.

Routes call get_users_db() or get_projects_db() rather than opening
their own connections. Tests swap extensions.MongoClient for an
in-memory stand-in.
"""

from pymongo import MongoClient

_users_db = None
_projects_db = None


def _open_client(uri, use_mock):
    if use_mock:
        import mongomock

        return mongomock.MongoClient()
    # Looked up on the module so tests can replace MongoClient.
    return MongoClient(uri)


def init_db(app):
    """Open the users database and the projects database.

    When both URIs match, both databases share one connection. When they
    differ, each cluster gets its own connection.
    """
    global _users_db, _projects_db
    use_mock = bool(app.config.get("USE_MOCK_DB"))
    users_uri = app.config.get("USERS_MONGO_URI") or app.config["MONGO_URI"]
    projects_uri = app.config.get("PROJECTS_MONGO_URI") or app.config["MONGO_URI"]

    users_client = _open_client(users_uri, use_mock)
    if projects_uri == users_uri:
        projects_client = users_client
    else:
        projects_client = _open_client(projects_uri, use_mock)

    _users_db = users_client[app.config["USERS_DB_NAME"]]
    _projects_db = projects_client[app.config["PROJECTS_DB_NAME"]]
    return _users_db, _projects_db


def get_users_db():
    """The database that holds the users collection."""
    if _users_db is None:
        raise RuntimeError("Database not initialized. Call init_db(app) first.")
    return _users_db


def get_projects_db():
    """The database that holds projects, hardware sets, and checkout history."""
    if _projects_db is None:
        raise RuntimeError("Database not initialized. Call init_db(app) first.")
    return _projects_db
