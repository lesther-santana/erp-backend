from argon2 import PasswordHasher
from argon2.exceptions import VerificationError


class Argon2Hashser:
    _hasher: PasswordHasher = PasswordHasher()

    @staticmethod
    def create_hash(password: str) -> str:
        """
        Hash a password.
        """
        return Argon2Hashser._hasher.hash(password)

    @staticmethod
    def verify(password_hash: str, password: str) -> bool:
        """
        Verify a password against a hash.
        """
        try:
            return Argon2Hashser._hasher.verify(password_hash, password)
        except VerificationError:
            return False
