from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

from FernetKeyGen.SaltManager import SaltManager


def derive_key(passphrase: str, generate_salt: bool = False, salt_path: str = '.salt') -> bytes:
    # Check if a passphrase is None or empty
    if passphrase is None or passphrase == "":
        return Fernet.generate_key()

    salt = SaltManager(generate_salt, salt_path)

    kdf2Hmac = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.get(),
        iterations=1000,
        backend=default_backend()
    )

    return base64.urlsafe_b64encode(kdf2Hmac.derive(passphrase.encode()))