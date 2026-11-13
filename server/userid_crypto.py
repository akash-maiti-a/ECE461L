"""Encrypt user IDs before they reach the users database (SR3: encrypt
the user ID and password).

Each account stores two values derived from its user ID, never the ID
itself:

- userid_hash: an HMAC-SHA256 of the ID. The same ID always gives the
  same hash, so sign-in can look an account up and sign-up can tell an ID
  is taken, without the database ever holding the ID.
- userid_encrypted: the ID encrypted with Fernet (AES-128 in CBC mode plus
  an HMAC). Anyone holding the key can decrypt it, so the ID can be
  recovered for an admin or a data export.

Both keys come from USERID_ENCRYPTION_KEY, which falls back to SECRET_KEY.
Changing it after accounts exist locks those accounts out, so set it once
per deployment and keep it out of the repo.
"""

import base64
import hashlib
import hmac

from cryptography.fernet import Fernet
from flask import current_app


def _subkey(label):
    master = current_app.config["USERID_ENCRYPTION_KEY"].encode()
    return hmac.new(master, label, hashlib.sha256).digest()


def userid_hash(userid):
    """The lookup value for this user ID. Exact match: "Alice" != "alice"."""
    return hmac.new(_subkey(b"userid-lookup"), userid.encode(), hashlib.sha256).hexdigest()


def _fernet():
    return Fernet(base64.urlsafe_b64encode(_subkey(b"userid-encrypt")))


def encrypt_userid(userid):
    return _fernet().encrypt(userid.encode()).decode()


def decrypt_userid(token):
    return _fernet().decrypt(token.encode()).decode()
