from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import os


# ---------------- KEY DERIVATION ----------------
def generate_key(password: str, salt: bytes) -> bytes:
    """
    Generate a secure key from password using PBKDF2.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


# ---------------- ENCRYPT ----------------
def encrypt_file(file_path: str, password: str) -> str:
    """
    Encrypt a file using a password.
    Stores salt + encrypted data in output file.
    """
    # Generate random salt
    salt = os.urandom(16)

    # Derive key
    key = generate_key(password, salt)
    fernet = Fernet(key)

    # Read file
    with open(file_path, 'rb') as f:
        data = f.read()

    # Encrypt
    encrypted_data = fernet.encrypt(data)

    # Output file
    encrypted_path = file_path + ".enc"

    # Store salt + encrypted data
    with open(encrypted_path, 'wb') as f:
        f.write(salt + encrypted_data)

    return encrypted_path


# ---------------- DECRYPT ----------------
def decrypt_file(file_path: str, password: str, output_path: str = None) -> str:
    """
    Decrypt a file using a password.
    Extracts salt from file before decrypting.
    """
    # Read file
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Extract salt + encrypted data
    salt = file_data[:16]
    encrypted_data = file_data[16:]

    # Derive key
    key = generate_key(password, salt)
    fernet = Fernet(key)

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception:
        raise Exception("Invalid password or corrupted file")

    # Output path handling
    if output_path is None:
        output_path = file_path.replace(".enc", "")

    # Write decrypted file
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)

    return output_path
