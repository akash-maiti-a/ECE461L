"""User account model (SR1, SR2: secure sign-up/sign-in).

A "model" here isn't an ORM class — MongoDB documents are just dicts.
Each model is a thin wrapper of static methods around one collection,
so route code never touches collection names or query syntax directly.
"""

import re

from werkzeug.security import check_password_hash, generate_password_hash


class User:
    collection_name = "users"

    @staticmethod
    def create(db, userid, password):
        """Create a new user with a hashed password.

        Returns the userid on success, or None if that userid is taken.
        The plaintext password is never stored — only its hash (SR2).
        """
        collection = db[User.collection_name]
        if collection.find_one({"userid": userid}):
            return None
        collection.insert_one(
            {
                "userid": userid,
                "password_hash": generate_password_hash(password),
            }
        )
        return userid

    @staticmethod
    def verify(db, userid, password):
        """Return True if userid exists and password matches its hash."""
        user = db[User.collection_name].find_one({"userid": userid})
        if not user:
            return False
        return check_password_hash(user["password_hash"], password)

    @staticmethod
    def find(db, userid):
        """The account with this user ID, or None.

        An exact match wins. Otherwise a case-insensitive match, so sharing
        "Alice" still finds the account stored as "alice". Only the userid
        comes back — never the password hash.
        """
        collection = db[User.collection_name]
        fields = {"_id": 0, "userid": 1}
        exact = collection.find_one({"userid": userid}, fields)
        if exact:
            return exact
        pattern = "^" + re.escape(userid) + "$"
        return collection.find_one({"userid": {"$regex": pattern, "$options": "i"}}, fields)

    @staticmethod
    def search(db, prefix, limit=8):
        """Accounts whose user ID starts with `prefix`, for the share field.

        The prefix is matched as plain text, not a regular expression, and
        only userids are returned. An empty prefix matches nobody, so the
        field doesn't download every account.
        """
        prefix = prefix.strip()
        if not prefix:
            return []
        pattern = "^" + re.escape(prefix)
        cursor = db[User.collection_name].find(
            {"userid": {"$regex": pattern, "$options": "i"}},
            {"_id": 0, "userid": 1},
        )
        matches = sorted(cursor, key=lambda user: user["userid"].lower())
        return matches[:limit]
