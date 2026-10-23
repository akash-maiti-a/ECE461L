"""Keeps users signed in with Flask's session cookie, which Flask signs
with SECRET_KEY so nobody can edit it to pretend to be someone else."""

from functools import wraps

from flask import jsonify, session


def current_userid():
    return session.get("userid")


def login_required(view):
    """Put this on any route that needs a signed-in user."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_userid():
            return jsonify({"error": "Your session has ended. Sign in again."}), 401
        return view(*args, **kwargs)

    return wrapped
