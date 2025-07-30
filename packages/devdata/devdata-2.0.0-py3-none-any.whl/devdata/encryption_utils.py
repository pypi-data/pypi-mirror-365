"""
encryption_utils.py

Robust data encryption/decryption utilities with AES-GCM and RSA,
including key management and file/bytes encryption support.

Dependencies:
- cryptography

Install with:
pip install cryptography
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import os
from typing import Optional, Tuple


# ----------------------------------------
# Symmetric Encryption (AES-GCM)
# ----------------------------------------

def generate_aes_key(length: int = 32) -> bytes:
    """
    Generate a secure random AES key.
    length: key length in bytes (default 32 for AES-256)
    """
    return os.urandom(length)


def aes_encrypt(plaintext: bytes, key: bytes, associated_data: Optional[bytes] = None) -> bytes:
    """
    Encrypt bytes with AES-GCM.
    Returns ciphertext including the nonce prepended (12 bytes nonce + ciphertext + tag).
    """
    nonce = os.urandom(12)  # 96-bit nonce recommended for AES-GCM
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return nonce + ciphertext


def aes_decrypt(ciphertext: bytes, key: bytes, associated_data: Optional[bytes] = None) -> bytes:
    """
    Decrypt AES-GCM encrypted bytes.
    Expects ciphertext with nonce prepended.
    """
    nonce = ciphertext[:12]
    actual_ct = ciphertext[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, actual_ct, associated_data)


# ----------------------------------------
# Password-Based Key Derivation (PBKDF2)
# ----------------------------------------

def derive_key_from_password(password: str, salt: bytes, length: int = 32, iterations: int = 100_000) -> bytes:
    """
    Derive AES key from password using PBKDF2-HMAC-SHA256.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations,
    )
    key = kdf.derive(password.encode('utf-8'))
    return key


# ----------------------------------------
# Asymmetric Encryption (RSA)
# ----------------------------------------

def generate_rsa_keypair(key_size: int = 2048) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """
    Generate RSA private and public key pair.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def rsa_encrypt(plaintext: bytes, public_key: rsa.RSAPublicKey) -> bytes:
    """
    Encrypt bytes with RSA public key using OAEP padding.
    """
    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext


def rsa_decrypt(ciphertext: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    """
    Decrypt bytes with RSA private key using OAEP padding.
    """
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext


# ----------------------------------------
# RSA Key Serialization / Deserialization
# ----------------------------------------

def serialize_private_key(private_key: rsa.RSAPrivateKey, password: Optional[bytes] = None) -> bytes:
    """
    Serialize private key to PEM format.
    If password is provided, the key is encrypted with it.
    """
    encryption_algorithm = (
        serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm,
    )


def deserialize_private_key(pem_data: bytes, password: Optional[bytes] = None) -> rsa.RSAPrivateKey:
    """
    Load private key from PEM bytes.
    """
    return serialization.load_pem_private_key(pem_data, password=password)


def serialize_public_key(public_key: rsa.RSAPublicKey) -> bytes:
    """
    Serialize public key to PEM format.
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def deserialize_public_key(pem_data: bytes) -> rsa.RSAPublicKey:
    """
    Load public key from PEM bytes.
    """
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    return load_pem_public_key(pem_data)


# ----------------------------------------
# File Encryption / Decryption Helpers
# ----------------------------------------

def encrypt_file(input_path: str, output_path: str, key: bytes, associated_data: Optional[bytes] = None) -> None:
    """
    Encrypt a file using AES-GCM and write ciphertext to output_path.
    """
    with open(input_path, 'rb') as f:
        plaintext = f.read()
    ciphertext = aes_encrypt(plaintext, key, associated_data)
    with open(output_path, 'wb') as f:
        f.write(ciphertext)


def decrypt_file(input_path: str, output_path: str, key: bytes, associated_data: Optional[bytes] = None) -> None:
    """
    Decrypt AES-GCM encrypted file.
    """
    with open(input_path, 'rb') as f:
        ciphertext = f.read()
    plaintext = aes_decrypt(ciphertext, key, associated_data)
    with open(output_path, 'wb') as f:
        f.write(plaintext)


# ----------------------------------------
# Utility Functions
# ----------------------------------------

def generate_salt(length: int = 16) -> bytes:
    """
    Generate secure random salt for key derivation.
    """
    return os.urandom(length)


# ----------------------------------------
# Example usage
# ----------------------------------------

if __name__ == "__main__":
    # Symmetric encryption demo
    key = generate_aes_key()
    message = b"Secret message for AES-GCM encryption"
    print("Original:", message)
    encrypted = aes_encrypt(message, key)
    decrypted = aes_decrypt(encrypted, key)
    print("Decrypted:", decrypted)

    # Password-based key derivation demo
    password = "supersecret"
    salt = generate_salt()
    derived_key = derive_key_from_password(password, salt)
    assert len(derived_key) == 32

    # RSA encryption demo
    priv_key, pub_key = generate_rsa_keypair()
    rsa_ciphertext = rsa_encrypt(message, pub_key)
    rsa_plaintext = rsa_decrypt(rsa_ciphertext, priv_key)
    print("RSA Decrypted:", rsa_plaintext)

    # Serialization demo
    priv_pem = serialize_private_key(priv_key, password=b"mypassword")
    pub_pem = serialize_public_key(pub_key)
    loaded_priv_key = deserialize_private_key(priv_pem, password=b"mypassword")
    loaded_pub_key = deserialize_public_key(pub_pem)
    assert rsa_decrypt(rsa_encrypt(b"test", loaded_pub_key), loaded_priv_key) == b"test"
