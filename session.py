import json

from cryptography.fernet import Fernet, InvalidToken


class SessionCipher:
    def __init__(self, key):
        if not isinstance(key, str) or not key.strip():
            raise RuntimeError("SESSION_ENCRYPTION_KEY is required")
        try:
            self._fernet = Fernet(key.strip().encode("ascii"))
        except (TypeError, ValueError) as error:
            raise RuntimeError("SESSION_ENCRYPTION_KEY must be a Fernet key") from error

    def encrypt_user(self, user):
        session = {
            "id": str(user["id"]),
            "name": str(user["name"]),
            "access_token": str(user["access_token"]),
        }
        payload = json.dumps(session, separators=(",", ":")).encode("utf-8")
        return self._fernet.encrypt(payload).decode("ascii")

    def decrypt_user(self, value):
        try:
            payload = self._fernet.decrypt(value.encode("ascii"))
            session = json.loads(payload.decode("utf-8"))
        except (InvalidToken, UnicodeError, ValueError, TypeError):
            return None
        if not isinstance(session, dict):
            return None
        if not all(isinstance(session.get(key), str) and session[key] for key in ("id", "name", "access_token")):
            return None
        return session
