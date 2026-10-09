"""User account model (SR1, SR2: secure sign-up/sign-in).

A "model" here isn't an ORM class — MongoDB documents are just dicts.
Each model is a thin wrapper of static methods around one collection,
so route code never touches collection names or query syntax directly.
"""

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
