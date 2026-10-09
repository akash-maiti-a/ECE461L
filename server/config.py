import os


class Config:
    """App configuration, pulled from environment variables.

    Keeping these in one place (rather than scattered through the app)
    means Phase 2 cloud deployment only has to set environment variables,
    not edit code.
    """

    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/haas_db")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
