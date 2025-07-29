from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

from SaltManager import SaltManager

def derive_key(passphrase, generate_salt=False):
    salt = SaltManager(generate_salt)

    kdf2Hmac = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.get(),
        iterations=1000,
        backend=default_backend()
    )

    return base64.urlsafe_b64encode(kdf2Hmac.derive(passphrase))