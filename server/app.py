"""Flask application entry point.

Run locally with:  python app.py
(requires a Mongo instance reachable at MONGO_URI, see .env.example,
or USE_MOCK_DB=1 for an in-memory database). Accounts and projects are
stored in separate databases.
"""

import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from extensions import get_projects_db, get_users_db, init_db
from models.hardware import Hardware
from models.user import User
from routes.auth import auth_bp
from routes.hardware import hardware_bp
from routes.projects import projects_bp


def create_app(config_class=Config):
    """Application factory. Building the app in a function (instead of
    at module scope) is what lets tests create a fresh app wired to a
    fake database, instead of always hitting a real Mongo instance.
    """
    # No Flask static folder: its /static route would hide the React
    # build's /static/js and /static/css files.
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)

    # Allow the React dev server (and the deployed frontend) to call this
    # API from a different origin.
    CORS(app, supports_credentials=True)

    init_db(app)
    Hardware.seed(get_projects_db())
    User.ensure_indexes(get_users_db())

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(hardware_bp)

    @app.route("/api/health")
    def health():
        return {
            "status": "ok",
            "usersDb": app.config["USERS_DB_NAME"],
            "projectsDb": app.config["PROJECTS_DB_NAME"],
        }, 200

    _serve_frontend(app)
    return app


def _serve_frontend(app):
    """Serve the React build at every path the API doesn't use (R2-3).

    One server for both means one URL for the TAs, and the sign-in cookie
    is same-site, so it is always sent. Paths that aren't files get
    index.html, so a refresh on any page still loads the app. Unknown /api
    paths get a JSON 404, since the frontend expects JSON from the API.
    """
    build_dir = app.config.get("FRONTEND_BUILD_DIR")
    has_build = bool(build_dir) and os.path.isfile(os.path.join(build_dir, "index.html"))

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def frontend(path):
        if path == "api" or path.startswith("api/") or not has_build:
            return jsonify({"error": "Not found."}), 404
        if path and os.path.isfile(os.path.join(build_dir, path)):
            # send_from_directory refuses paths that climb out of build_dir.
            return send_from_directory(build_dir, path)
        return send_from_directory(build_dir, "index.html")


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=app.config["PORT"])
