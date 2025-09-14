# encryption.py
from cryptography.fernet import Fernet
import base64
import hashlib
import os

def generate_key(password: str) -> bytes:
    """Generate a Fernet-compatible key from the password"""
    # Use SHA256 to create a 32-byte key and then base64 encode
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def encrypt_file(file_path, password):
    key = generate_key(password)
    fernet = Fernet(key)

    with open(file_path, 'rb') as f:
        data = f.read()
    
    encrypted = fernet.encrypt(data)

    encrypted_path = file_path + ".enc"
    with open(encrypted_path, 'wb') as f:
        f.write(encrypted)
    
    return encrypted_path

def decrypt_file(file_path, password, output_path=None):
    key = generate_key(password)
    fernet = Fernet(key)

    with open(file_path, 'rb') as f:
        encrypted = f.read()
    
    decrypted = fernet.decrypt(encrypted)

    if output_path is None:
        if file_path.endswith(".enc"):
            output_path = file_path[:-4] + ".dec"
        else:
            output_path = file_path + ".dec"

    with open(output_path, 'wb') as f:
        f.write(decrypted)
    
    return output_path
