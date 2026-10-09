"""Flask application entry point.

Run locally with:  python app.py
(requires a Mongo instance reachable at MONGO_URI, see .env.example)
"""

from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import init_db
from models.hardware import Hardware
from routes.auth import auth_bp
from routes.hardware import hardware_bp
from routes.projects import projects_bp


def create_app(config_class=Config):
    """Application factory. Building the app in a function (instead of
    at module scope) is what lets tests create a fresh app wired to a
    fake database, instead of always hitting a real Mongo instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Allow the React dev server (and the deployed frontend) to call this
    # API from a different origin.
    CORS(app)

    db = init_db(app)
    Hardware.seed(db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(hardware_bp)

    @app.route("/api/health")
    def health():
        return {"status": "ok"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
