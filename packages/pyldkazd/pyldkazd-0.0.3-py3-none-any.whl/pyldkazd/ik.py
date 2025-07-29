"""
In-memory identity & session key store for Discord bot group key exchange.

Implements minimal Signal Protocol-like in-memory storage for key material,
modeled after Signal's InMemSignalProtocolStore, adapted for Python.

Usage:
    store = InMemProtocolStore(identity_keypair, registration_id)
"""

from typing import Dict, Optional
from collections import deque

class InMemIdentityKeyStore:
    def __init__(self, identity_keypair, registration_id: int):
        self.key_pair = identity_keypair  # Instance of your IdentityKeyPair class
        self.id = registration_id
        self.known_keys: Dict[str, bytes] = {}

    def get_identity_key_pair(self):
        return self.key_pair

    def get_local_registration_id(self):
        return self.id

    def save_identity(self, address: str, identity: bytes) -> bool:
        prev = self.known_keys.get(address)
        self.known_keys[address] = identity
        return prev is not None and prev != identity

    def is_trusted_identity(self, address: str, identity: bytes) -> bool:
        prev = self.known_keys.get(address)
        return prev is None or prev == identity

    def get_identity(self, address: str) -> Optional[bytes]:
        return self.known_keys.get(address)


class InMemSessionStore:
    def __init__(self):
        self.sessions: Dict[str, bytes] = {}

    def load_session(self, address: str) -> Optional[bytes]:
        return self.sessions.get(address)

    def store_session(self, address: str, record: bytes):
        self.sessions[address] = record


class InMemPreKeyStore:
    def __init__(self):
        self.pre_keys: Dict[int, bytes] = {}

    def get_pre_key(self, prekey_id: int) -> bytes:
        return self.pre_keys[prekey_id]

    def save_pre_key(self, prekey_id: int, record: bytes):
        self.pre_keys[prekey_id] = record

    def remove_pre_key(self, prekey_id: int):
        self.pre_keys.pop(prekey_id, None)


class InMemSignedPreKeyStore:
    def __init__(self):
        self.signed_pre_keys: Dict[int, bytes] = {}

    def get_signed_pre_key(self, signed_prekey_id: int) -> bytes:
        return self.signed_pre_keys[signed_prekey_id]

    def save_signed_pre_key(self, signed_prekey_id: int, record: bytes):
        self.signed_pre_keys[signed_prekey_id] = record


class InMemSenderKeyStore:
    def __init__(self):
        self.sender_keys: Dict[str, bytes] = {}

    def store_sender_key(self, sender_key_name: str, record: bytes):
        self.sender_keys[sender_key_name] = record

    def load_sender_key(self, sender_key_name: str) -> Optional[bytes]:
        return self.sender_keys.get(sender_key_name)


class InMemProtocolStore:
    """
    All-in-one store (like Signal InMemSignalProtocolStore).
    """
    def __init__(self, identity_keypair, registration_id: int):
        self.identity_store = InMemIdentityKeyStore(identity_keypair, registration_id)
        self.session_store = InMemSessionStore()
        self.pre_key_store = InMemPreKeyStore()
        self.signed_pre_key_store = InMemSignedPreKeyStore()
        self.sender_key_store = InMemSenderKeyStore()
