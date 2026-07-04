import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from ..config import get_settings

settings = get_settings()

_SALT = b"my_tools_db_conn_salt_2024"


def _get_cipher() -> Fernet:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.db_cipher_key.encode("utf-8")))
    return Fernet(key)


def encrypt_password(plain_password: str) -> str:
    if not plain_password:
        return ""
    cipher = _get_cipher()
    return cipher.encrypt(plain_password.encode("utf-8")).decode("utf-8")


def decrypt_password(encrypted_password: str) -> str:
    if not encrypted_password:
        return ""
    cipher = _get_cipher()
    return cipher.decrypt(encrypted_password.encode("utf-8")).decode("utf-8")
