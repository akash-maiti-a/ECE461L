"""Flask serves the React build next to the API, so the deployed app is one
URL and the sign-in cookie stays same-site (#37)."""

import pytest

import extensions
import mongomock
from app import create_app
from config import Config


@pytest.fixture
def build_dir(tmp_path):
    """A stand-in for creator-eaas/build with a page and one JS file."""
    (tmp_path / "index.html").write_text("<html>Creator EaaS</html>")
    (tmp_path / "static" / "js").mkdir(parents=True)
    (tmp_path / "static" / "js" / "main.js").write_text("console.log('app');")
    return tmp_path


@pytest.fixture
def site(monkeypatch, build_dir):
    monkeypatch.setattr(extensions, "MongoClient", mongomock.MongoClient)
    monkeypatch.setattr(Config, "MONGO_URI", "mongodb://localhost:27017/haas_db")
    monkeypatch.setattr(Config, "USERS_MONGO_URI", None)
    monkeypatch.setattr(Config, "PROJECTS_MONGO_URI", None)
    monkeypatch.setattr(Config, "HARDWARE_MONGO_URI", None)
    monkeypatch.setattr(Config, "FRONTEND_BUILD_DIR", str(build_dir))
    return create_app().test_client()


def test_root_serves_the_page(site):
    response = site.get("/")
    assert response.status_code == 200
    assert b"Creator EaaS" in response.data


def test_build_files_are_served(site):
    response = site.get("/static/js/main.js")
    assert response.status_code == 200
    assert b"console.log" in response.data


def test_other_paths_get_the_page_so_refresh_works(site):
    response = site.get("/projects/film-01")
    assert response.status_code == 200
    assert b"Creator EaaS" in response.data


def test_api_still_works_alongside_the_page(site):
    assert site.get("/api/health").get_json()["status"] == "ok"
    assert site.get("/api/hardware").status_code == 200


def test_unknown_api_paths_get_json_404(site):
    response = site.get("/api/nope")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not found."}


def test_paths_cannot_escape_the_build_folder(site, build_dir):
    (build_dir.parent / "secret.txt").write_text("do not serve")
    for path in ["/../secret.txt", "/static/../../secret.txt", "/%2e%2e/secret.txt"]:
        response = site.get(path)
        assert b"do not serve" not in response.data, path


def test_without_a_build_only_the_api_runs(monkeypatch, tmp_path):
    monkeypatch.setattr(extensions, "MongoClient", mongomock.MongoClient)
    monkeypatch.setattr(Config, "MONGO_URI", "mongodb://localhost:27017/haas_db")
    monkeypatch.setattr(Config, "USERS_MONGO_URI", None)
    monkeypatch.setattr(Config, "PROJECTS_MONGO_URI", None)
    monkeypatch.setattr(Config, "HARDWARE_MONGO_URI", None)
    monkeypatch.setattr(Config, "FRONTEND_BUILD_DIR", str(tmp_path / "missing"))
    browser = create_app().test_client()

    assert browser.get("/").status_code == 404
    assert browser.get("/api/health").status_code == 200


def test_sign_in_cookie_is_https_only_when_configured(monkeypatch):
    monkeypatch.setattr(extensions, "MongoClient", mongomock.MongoClient)
    monkeypatch.setattr(Config, "MONGO_URI", "mongodb://localhost:27017/haas_db")
    monkeypatch.setattr(Config, "USERS_MONGO_URI", None)
    monkeypatch.setattr(Config, "PROJECTS_MONGO_URI", None)
    monkeypatch.setattr(Config, "HARDWARE_MONGO_URI", None)
    monkeypatch.setattr(Config, "SESSION_COOKIE_SECURE", True)
    browser = create_app().test_client()

    response = browser.post("/api/auth/signup", json={"userid": "sam", "password": "sam-pass1"})

    cookie = response.headers["Set-Cookie"]
    assert "Secure" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
