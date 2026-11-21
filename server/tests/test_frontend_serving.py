"""Flask serves the React build so the deployed app has one URL (R2-3)."""

import mongomock
import pytest

import extensions
from app import create_app
from config import Config


@pytest.fixture
def build_dir(tmp_path):
    (tmp_path / "index.html").write_text("<!doctype html><div id=root></div>")
    (tmp_path / "static" / "js").mkdir(parents=True)
    (tmp_path / "static" / "js" / "main.js").write_text("console.log('hi')")
    return tmp_path


def _make_app(monkeypatch, build_dir):
    monkeypatch.setattr(extensions, "MongoClient", mongomock.MongoClient)
    monkeypatch.setattr(Config, "MONGO_URI", "mongodb://localhost:27017")
    monkeypatch.setattr(Config, "USERS_MONGO_URI", None)
    monkeypatch.setattr(Config, "PROJECTS_MONGO_URI", None)
    monkeypatch.setattr(Config, "FRONTEND_BUILD_DIR", str(build_dir))
    return create_app().test_client()


def test_root_serves_index(monkeypatch, build_dir):
    response = _make_app(monkeypatch, build_dir).get("/")
    assert response.status_code == 200
    assert b"id=root" in response.data


def test_static_files_are_served(monkeypatch, build_dir):
    response = _make_app(monkeypatch, build_dir).get("/static/js/main.js")
    assert response.status_code == 200
    assert b"console.log" in response.data


def test_unknown_page_falls_back_to_index(monkeypatch, build_dir):
    response = _make_app(monkeypatch, build_dir).get("/projects/some-page")
    assert response.status_code == 200
    assert b"id=root" in response.data


def test_api_routes_still_win(monkeypatch, build_dir):
    response = _make_app(monkeypatch, build_dir).get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_unknown_api_path_is_json_404(monkeypatch, build_dir):
    response = _make_app(monkeypatch, build_dir).get("/api/nope")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not found."}


def test_paths_cannot_escape_build_dir(monkeypatch, build_dir):
    (build_dir.parent / "secret.txt").write_text("do not serve")
    response = _make_app(monkeypatch, build_dir).get("/..%2fsecret.txt")
    assert b"do not serve" not in response.data


def test_without_a_build_only_the_api_runs(monkeypatch, tmp_path):
    client = _make_app(monkeypatch, tmp_path / "missing")
    assert client.get("/").status_code == 404
    assert client.get("/api/health").status_code == 200
