"""
crypto.py — Core cryptography module for VaultPy
-------------------------------------------------
Handles:
  - Argon2id key derivation from master password
  - AES-256-GCM authenticated encryption / decryption
  - Secure salt and nonce generation
"""

import os
import json
import base64
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# --- Argon2id Parameters (tuned for security vs speed) ---
ARGON2_TIME_COST    = 3        # iterations
ARGON2_MEMORY_COST  = 65536   # 64 MB
ARGON2_PARALLELISM  = 4
ARGON2_HASH_LEN     = 32       # 256-bit key output
ARGON2_SALT_LEN     = 16       # 128-bit salt

# --- AES-GCM Parameters ---
NONCE_LEN = 12   # 96-bit nonce (recommended for GCM)


def generate_salt() -> bytes:
    """Generate a cryptographically secure random salt."""
    return os.urandom(ARGON2_SALT_LEN)


def derive_key(master_password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit encryption key from the master password using Argon2id.
    
    Args:
        master_password: The user's master password (string)
        salt: Random salt bytes (generated once, stored in vault file)
    
    Returns:
        32-byte derived key (never stored, only kept in memory)
    """
    key = hash_secret_raw(
        secret=master_password.encode("utf-8"),
        salt=salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=ARGON2_HASH_LEN,
        type=Type.ID   # Argon2id variant
    )
    return key


def encrypt(plaintext: str, key: bytes) -> dict:
    """
    Encrypt plaintext using AES-256-GCM authenticated encryption.
    
    Args:
        plaintext: String data to encrypt (your vault JSON)
        key: 32-byte derived key from derive_key()
    
    Returns:
        Dict with nonce and ciphertext (both base64-encoded for storage)
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_LEN)                          # fresh nonce every time
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    return {
        "nonce":      base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
        # Note: AESGCM appends the 16-byte auth tag to ciphertext automatically
    }


def decrypt(encrypted: dict, key: bytes) -> str:
    """
    Decrypt and verify AES-256-GCM ciphertext.
    
    Args:
        encrypted: Dict with 'nonce' and 'ciphertext' (base64 strings)
        key: 32-byte derived key from derive_key()
    
    Returns:
        Decrypted plaintext string
    
    Raises:
        cryptography.exceptions.InvalidTag: If decryption fails (wrong key or tampered data)
    """
    aesgcm = AESGCM(key)
    nonce      = base64.b64decode(encrypted["nonce"])
    ciphertext = base64.b64decode(encrypted["ciphertext"])
    plaintext  = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")


def wipe_key(key: bytearray) -> None:
    """
    Overwrite key material in memory before discarding.
    Call this when locking the vault or on app shutdown.
    """
    if isinstance(key, bytearray):
        for i in range(len(key)):
            key[i] = 0
