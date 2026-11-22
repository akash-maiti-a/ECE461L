"""Flask application entry point.

Run locally with:  python app.py
(requires a Mongo instance reachable at MONGO_URI, see .env.example,
or USE_MOCK_DB=1 for an in-memory database). Accounts and projects are
stored in separate databases.
"""

import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import safe_join

from config import Config
from extensions import get_hardware_db, get_projects_db, get_users_db, init_db
from hardware_migration import copy_hardware_from_projects_db
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
    # No Flask static folder: its /static route would hide the React build's
    # /static/js and /static/css files.
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)

    # Allow the React dev server (and the deployed frontend) to call this
    # API from a different origin.
    CORS(app, supports_credentials=True)

    init_db(app)
    # Copy any existing hardware data over before seeding, so a deployment
    # that already has kits out keeps its live counts.
    copy_hardware_from_projects_db(get_projects_db(), get_hardware_db())
    Hardware.seed(get_hardware_db())
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
            "hardwareDb": app.config["HARDWARE_DB_NAME"],
        }, 200

    _serve_frontend(app)
    return app


def _serve_frontend(app):
    """Serve the React build at every path the API doesn't use (R2-3).

    Serving the page and the API from one server gives the TAs one URL, and
    keeps the sign-in cookie same-site so browsers always send it (#37).

    - A path that is a file in the build (like /static/js/main.js) gets that
      file. safe_join refuses paths that would climb out of the build folder.
    - Any other path gets index.html, so refreshing on any page still loads
      the app.
    - Unknown /api paths get a JSON 404, since the frontend expects JSON.
    - Without a build (local development, where npm start serves the page),
      everything here is a JSON 404 and only the API runs.
    """

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def frontend(path):
        not_found = jsonify({"error": "Not found."}), 404
        if path == "api" or path.startswith("api/"):
            return not_found
        build_dir = app.config.get("FRONTEND_BUILD_DIR")
        if not build_dir or not os.path.isfile(os.path.join(build_dir, "index.html")):
            return not_found
        file_path = safe_join(build_dir, path) if path else None
        if file_path and os.path.isfile(file_path):
            return send_from_directory(build_dir, path)
        return send_from_directory(build_dir, "index.html")


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=app.config["PORT"])
