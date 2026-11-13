"""User account model (SR1, SR3: secure sign-up/sign-in).

A "model" here isn't an ORM class — MongoDB documents are just dicts.
Each model is a thin wrapper of static methods around one collection,
so route code never touches collection names or query syntax directly.

Neither the user ID nor the password is stored as typed:
- the user ID is kept as a keyed hash (for lookups) and as ciphertext
  (see userid_crypto.py);
- the password is kept only as a salted hash.

Accounts created before user IDs were encrypted have a plain `userid`
field. They still sign in, and are converted the first time they do.
"""

from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash

from userid_crypto import encrypt_userid, userid_hash


class User:
    collection_name = "users"

    @staticmethod
    def ensure_indexes(db):
        """One account per user ID, even if two sign-ups race."""
        db[User.collection_name].create_index("userid_hash", unique=True, sparse=True)

    @staticmethod
    def create(db, userid, password):
        """Create a new user. Returns the userid on success, or None if
        that userid is taken.
        """
        collection = db[User.collection_name]
        lookup = userid_hash(userid)
        if collection.find_one({"userid_hash": lookup}) or collection.find_one({"userid": userid}):
            return None
        try:
            collection.insert_one(
                {
                    "userid_hash": lookup,
                    "userid_encrypted": encrypt_userid(userid),
                    "password_hash": generate_password_hash(password),
                }
            )
        except DuplicateKeyError:
            return None
        return userid

    @staticmethod
    def verify(db, userid, password):
        """Return True if userid exists and password matches its hash."""
        collection = db[User.collection_name]
        lookup = userid_hash(userid)
        user = collection.find_one({"userid_hash": lookup})
        if user:
            return check_password_hash(user["password_hash"], password)

        legacy = collection.find_one({"userid": userid})
        if not legacy or not check_password_hash(legacy["password_hash"], password):
            return False
        # Stored before encryption: swap the plain ID for the encrypted one.
        collection.update_one(
            {"_id": legacy["_id"]},
            {
                "$set": {"userid_hash": lookup, "userid_encrypted": encrypt_userid(userid)},
                "$unset": {"userid": ""},
            },
        )
        return True
