import os
from datetime import timedelta

from dotenv import load_dotenv

# Pull settings from server/.env if present (see .env.example).
load_dotenv()


class Config:
    """App configuration, pulled from environment variables.

    Keeping these in one place (rather than scattered through the app)
    means Phase 2 cloud deployment only has to set environment variables,
    not edit code.
    """

    # MONGODB_URI is the name MongoDB Atlas's onboarding writes into .env.
    # A database name in this URI is ignored. Accounts and projects use
    # USERS_DB_NAME and PROJECTS_DB_NAME so they stay in separate databases.
    MONGO_URI = (
        os.environ.get("MONGO_URI")
        or os.environ.get("MONGODB_URI")
        or "mongodb://localhost:27017"
    )
    # Set these to put accounts and projects on different clusters.
    # Left unset, both use MONGO_URI.
    USERS_MONGO_URI = os.environ.get("USERS_MONGO_URI") or None
    PROJECTS_MONGO_URI = os.environ.get("PROJECTS_MONGO_URI") or None
    USERS_DB_NAME = os.environ.get("USERS_DB_NAME") or "haas_users"
    PROJECTS_DB_NAME = os.environ.get("PROJECTS_DB_NAME") or "haas_projects"
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    # Port 5000 is taken by AirPlay Receiver on recent macOS, so default to 5001.
    PORT = int(os.environ.get("PORT", "5001"))
    # Set USE_MOCK_DB=1 to run against an in-memory database (no MongoDB
    # install needed). Data is lost when the server stops.
    USE_MOCK_DB = os.environ.get("USE_MOCK_DB") == "1"
    # Sign-in cookie lasts a week and isn't sent on requests from other sites.
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SAMESITE = "Lax"
