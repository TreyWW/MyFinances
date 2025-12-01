"""
Deterministic, reversible UUIDs for numeric IDs.

- get_uuid(id, model_name)    -> UUID (looks random)
- revert_uuid(uuid_obj)       -> original id

The AES key is provided via Django settings (UUID_AES_KEY).
Only the numeric ID is reversible; the model name is used only to diversify
the UUID via hashing.
"""

from __future__ import annotations

import hashlib
import struct
import uuid
from typing import Final

from django.conf import settings
from Crypto.Cipher import AES


BLOCK_SIZE: Final[int] = 16


def _get_aes_key() -> bytes:
    """
    Read the AES key from Django settings.
    """
    key = getattr(settings, "UUID_AES_KEY", None)
    if key is None:
        raise RuntimeError("UUID_AES_KEY must be defined in Django settings")

    if isinstance(key, str):
        key = key.encode("utf-8")

    if len(key) not in (16, 24, 32):
        raise ValueError("UUID_AES_KEY must be 16, 24, or 32 bytes long")

    return key


def _get_cipher() -> AES:
    key = _get_aes_key()
    return AES.new(key, AES.MODE_ECB)


def get_uuid(numeric_id: int, model_name: str) -> uuid.UUID:
    """
    Create a deterministic, reversible UUID from (numeric_id, model_name).

    Layout of the 16‑byte plaintext block before encryption:
        - first 8 bytes: numeric_id (unsigned, big‑endian)
        - next 8 bytes: first 8 bytes of SHA‑256(model_name)

    This block is encrypted with AES, and the ciphertext is used as the UUID
    bytes via uuid.UUID(bytes=...).
    """
    if numeric_id < 0:
        raise ValueError("numeric_id must be non-negative")

    id_bytes = struct.pack(">Q", numeric_id)
    name_hash = hashlib.sha256(model_name.encode("utf-8")).digest()[:8]

    plaintext = id_bytes + name_hash
    if len(plaintext) != BLOCK_SIZE:
        raise AssertionError("Plaintext must be exactly 16 bytes")

    cipher = _get_cipher()
    ciphertext = cipher.encrypt(plaintext)

    return uuid.UUID(bytes=ciphertext)


def revert_uuid(u: uuid.UUID) -> int:
    """
    Recover the numeric_id from a UUID produced by get_uuid().

    Only the first 8 decrypted bytes (the encoded numeric_id) are returned.
    The model name cannot be recovered from the UUID.
    """
    cipher = _get_cipher()
    plaintext = cipher.decrypt(u.bytes)

    id_bytes = plaintext[:8]
    (numeric_id,) = struct.unpack(">Q", id_bytes)

    return numeric_id
