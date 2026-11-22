"""Shared database connections.

Accounts, projects, and hardware each live in their own database: users,
projects, and hardware sets with their checkout history. The three can
sit on one MongoDB cluster or on different clusters, depending on the
URIs in the config.

Routes call get_users_db(), get_projects_db(), or get_hardware_db()
rather than opening their own connections. Tests swap
extensions.MongoClient for an in-memory stand-in.
"""

from pymongo import MongoClient

_users_db = None
_projects_db = None
_hardware_db = None


def _open_client(uri, use_mock):
    if use_mock:
        import mongomock

        return mongomock.MongoClient()
    # Looked up on the module so tests can replace MongoClient.
    return MongoClient(uri)


def init_db(app):
    """Open the users, projects, and hardware databases.

    Databases whose URIs match share one connection; each different URI
    gets its own.
    """
    global _users_db, _projects_db, _hardware_db
    use_mock = bool(app.config.get("USE_MOCK_DB"))
    default_uri = app.config["MONGO_URI"]
    uris = {
        "users": app.config.get("USERS_MONGO_URI") or default_uri,
        "projects": app.config.get("PROJECTS_MONGO_URI") or default_uri,
        "hardware": app.config.get("HARDWARE_MONGO_URI") or default_uri,
    }

    clients = {}
    for uri in uris.values():
        if uri not in clients:
            clients[uri] = _open_client(uri, use_mock)

    _users_db = clients[uris["users"]][app.config["USERS_DB_NAME"]]
    _projects_db = clients[uris["projects"]][app.config["PROJECTS_DB_NAME"]]
    _hardware_db = clients[uris["hardware"]][app.config["HARDWARE_DB_NAME"]]
    return _users_db, _projects_db, _hardware_db


def _require(db):
    if db is None:
        raise RuntimeError("Database not initialized. Call init_db(app) first.")
    return db


def get_users_db():
    """The database that holds the users collection."""
    return _require(_users_db)


def get_projects_db():
    """The database that holds projects and their checkout tallies."""
    return _require(_projects_db)


def get_hardware_db():
    """The database that holds hardware sets and checkout history."""
    return _require(_hardware_db)
