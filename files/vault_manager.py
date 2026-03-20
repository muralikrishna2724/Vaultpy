"""
vault_manager.py — Vault file read/write logic
-----------------------------------------------
The vault file (~/.vaultpy/vault.enc) is a JSON file structured as:

{
  "kdf": "argon2id",
  "kdf_params": { "t": 3, "m": 65536, "p": 4 },
  "salt": "<base64>",
  "nonce": "<base64>",
  "ciphertext": "<base64>"
}

The encrypted payload is a JSON array of password entries:
[
  {
    "id": "uuid",
    "title": "GitHub",
    "username": "alice@email.com",
    "password": "s3cr3t",
    "url": "https://github.com",
    "notes": ""
  },
  ...
]
"""

import os
import json
import base64
import uuid
from pathlib import Path
from cryptography.exceptions import InvalidTag
from crypto import derive_key, encrypt, decrypt, generate_salt


# Default vault location: ~/.vaultpy/vault.enc
VAULT_DIR  = Path.home() / ".vaultpy"
VAULT_FILE = VAULT_DIR / "vault.enc"


class VaultManager:
    """
    Manages the encrypted vault file and in-memory vault state.
    
    Usage:
        vm = VaultManager()
        
        # First time — create vault
        vm.create_vault("my_master_password")
        
        # Later — unlock existing vault
        vm.unlock("my_master_password")
        entries = vm.get_entries()
        
        # Add a new entry
        vm.add_entry("GitHub", "alice@email.com", "s3cr3t", "https://github.com")
        
        # Save and lock
        vm.save()
        vm.lock()
    """

    def __init__(self):
        self._key: bytes | None = None          # Derived key, lives in memory only
        self._entries: list[dict] = []           # Decrypted vault entries
        self._salt: bytes | None = None          # Stored in vault file
        self._unlocked: bool = False

    # ------------------------------------------------------------------ #
    #  Vault lifecycle                                                     #
    # ------------------------------------------------------------------ #

    def vault_exists(self) -> bool:
        return VAULT_FILE.exists()

    def create_vault(self, master_password: str) -> None:
        """Create a brand new empty vault with a fresh salt."""
        VAULT_DIR.mkdir(parents=True, exist_ok=True)

        self._salt    = generate_salt()
        self._key     = derive_key(master_password, self._salt)
        self._entries = []
        self._unlocked = True

        self.save()

        # Lock down file permissions (owner read/write only)
        os.chmod(VAULT_FILE, 0o600)

    def unlock(self, master_password: str) -> bool:
        """
        Derive key from master password and decrypt vault.
        Returns True on success, False on wrong password.
        """
        if not self.vault_exists():
            raise FileNotFoundError("No vault found. Create one first.")

        with open(VAULT_FILE, "r") as f:
            vault_data = json.load(f)

        self._salt = base64.b64decode(vault_data["salt"])
        self._key  = derive_key(master_password, self._salt)

        try:
            plaintext = decrypt(
                {"nonce": vault_data["nonce"], "ciphertext": vault_data["ciphertext"]},
                self._key
            )
            self._entries  = json.loads(plaintext)
            self._unlocked = True
            return True

        except InvalidTag:
            # Wrong password or tampered file
            self._key     = None
            self._entries = []
            return False

    def lock(self) -> None:
        """Wipe key and entries from memory."""
        self._key      = None
        self._entries  = []
        self._unlocked = False

    def save(self) -> None:
        """Encrypt and write vault to disk."""
        if not self._unlocked or self._key is None:
            raise PermissionError("Vault is locked.")

        plaintext   = json.dumps(self._entries)
        encrypted   = encrypt(plaintext, self._key)

        vault_data = {
            "kdf": "argon2id",
            "kdf_params": {"t": 3, "m": 65536, "p": 4},
            "salt":       base64.b64encode(self._salt).decode(),
            "nonce":      encrypted["nonce"],
            "ciphertext": encrypted["ciphertext"]
        }

        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        with open(VAULT_FILE, "w") as f:
            json.dump(vault_data, f, indent=2)

    # ------------------------------------------------------------------ #
    #  Entry CRUD                                                          #
    # ------------------------------------------------------------------ #

    def get_entries(self) -> list[dict]:
        return self._entries.copy()

    def add_entry(self, title: str, username: str, password: str,
                  url: str = "", notes: str = "") -> dict:
        entry = {
            "id":       str(uuid.uuid4()),
            "title":    title,
            "username": username,
            "password": password,
            "url":      url,
            "notes":    notes
        }
        self._entries.append(entry)
        self.save()
        return entry

    def update_entry(self, entry_id: str, **fields) -> bool:
        for entry in self._entries:
            if entry["id"] == entry_id:
                entry.update(fields)
                self.save()
                return True
        return False

    def delete_entry(self, entry_id: str) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e["id"] != entry_id]
        if len(self._entries) < before:
            self.save()
            return True
        return False

    def get_entry(self, entry_id: str) -> dict | None:
        return next((e for e in self._entries if e["id"] == entry_id), None)

    @property
    def is_unlocked(self) -> bool:
        return self._unlocked
