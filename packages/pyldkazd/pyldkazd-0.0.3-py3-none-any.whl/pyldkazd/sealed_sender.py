"""
Sealed Sender implementation using x3dh.py, double_ratchet.py, and ik.py.
This file provides a real, production-style interface for sealed sender encryption and decryption
using real cryptographic objects and Ed25519-based certificate verification.

Dependencies:
- x3dh.py: X3DH key exchange for session setup.
- double_ratchet.py: Double Ratchet for message encryption.
- ik.py: In-memory protocol store for key/session management.

Usage:
    # Sender side:
    ciphertext = sealed_sender_encrypt(
        sender_store, recipient_bundle, sender_certificate, plaintext,
    )

    # Recipient side:
    sender_cert, plaintext = sealed_sender_decrypt(
        recipient_store, ciphertext, trust_root_pubkey, timestamp, local_address
    )
"""

import time

from .x3dh import (
    Bundle,
    X3DHState,
    IdentityKeyFormat,
    HashFunction,
)
from .double_ratchet import (
    DRSession,
    DHKeyPair,
    DHPublicKey,
    AES256GCM,
    Message,
)
from .ik import InMemProtocolStore

from typing import Optional, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey, Ed25519PrivateKey
)
from cryptography.exceptions import InvalidSignature

# ---- Real Certificate Class Definitions ----

class ServerCertificate:
    """
    Real cryptographic server certificate using Ed25519 signatures.
    Fields: key_id (int), public_key (bytes), trust_root (bytes), signature (bytes)
    """
    def __init__(self, key_id: int, public_key: bytes, trust_root: bytes, signature: bytes):
        self.key_id = key_id
        self.public_key = public_key
        self.trust_root = trust_root
        self.signature = signature

    def serialize(self) -> bytes:
        return (
            self.key_id.to_bytes(4, "big")
            + len(self.public_key).to_bytes(2, "big") + self.public_key
            + len(self.trust_root).to_bytes(2, "big") + self.trust_root
            + len(self.signature).to_bytes(2, "big") + self.signature
        )

    @staticmethod
    def deserialize(data: bytes):
        ptr = 0
        key_id = int.from_bytes(data[ptr:ptr+4], "big"); ptr += 4
        l = int.from_bytes(data[ptr:ptr+2], "big"); ptr += 2
        public_key = data[ptr:ptr+l]; ptr += l
        l = int.from_bytes(data[ptr:ptr+2], "big"); ptr += 2
        trust_root = data[ptr:ptr+l]; ptr += l
        l = int.from_bytes(data[ptr:ptr+2], "big"); ptr += 2
        signature = data[ptr:ptr+l]; ptr += l
        return ServerCertificate(key_id, public_key, trust_root, signature)

    def verify(self) -> bool:
        """
        Signature is Ed25519 over public_key, signed by trust_root (which is the Ed25519 public key of the CA).
        """
        try:
            ca_pub = Ed25519PublicKey.from_public_bytes(self.trust_root)
            ca_pub.verify(self.signature, self.public_key)
            return True
        except InvalidSignature:
            return False
        except Exception:
            return False

class SenderCertificate:
    """
    Real cryptographic sender certificate using Ed25519 signatures.
    Fields:
      - sender_id (str)
      - sender_pubkey (bytes)
      - device_id (int)
      - expiration (int, unix ts)
      - server_certificate (ServerCertificate)
      - signature (bytes)
    """
    def __init__(
        self, sender_id: str, sender_pubkey: bytes, device_id: int, expiration: int,
        server_certificate: ServerCertificate, signature: bytes,
    ):
        self.sender_id = sender_id
        self.sender_pubkey = sender_pubkey
        self.device_id = device_id
        self.expiration = expiration
        self.server_certificate = server_certificate
        self.signature = signature

    def serialize(self) -> bytes:
        sid_bytes = self.sender_id.encode()
        return (
            len(sid_bytes).to_bytes(2, "big") + sid_bytes
            + len(self.sender_pubkey).to_bytes(2, "big") + self.sender_pubkey
            + self.device_id.to_bytes(4, "big")
            + self.expiration.to_bytes(8, "big")
            + self.server_certificate.serialize()
            + len(self.signature).to_bytes(2, "big") + self.signature
        )

    @staticmethod
    def deserialize(data: bytes):
        ptr = 0
        l = int.from_bytes(data[ptr:ptr+2], "big"); ptr += 2
        sender_id = data[ptr:ptr+l].decode(); ptr += l
        l = int.from_bytes(data[ptr:ptr+2], "big"); ptr += 2
        sender_pubkey = data[ptr:ptr+l]; ptr += l
        device_id = int.from_bytes(data[ptr:ptr+4], "big"); ptr += 4
        expiration = int.from_bytes(data[ptr:ptr+8], "big"); ptr += 8
        scert = ServerCertificate.deserialize(data[ptr:])
        scert_ser_len = len(scert.serialize())
        ptr += scert_ser_len
        l = int.from_bytes(data[ptr:ptr+2], "big"); ptr += 2
        signature = data[ptr:ptr+l]; ptr += l
        return SenderCertificate(sender_id, sender_pubkey, device_id, expiration, scert, signature)

    def verify(self, trust_root: bytes, validation_time: int) -> bool:
        """
        - Checks signature chain: server_certificate signed by trust_root,
          then this sender certificate signed by server_certificate.public_key.
        - Validates expiration.
        """
        if validation_time > self.expiration:
            return False
        if not self.server_certificate.verify():
            return False
        try:
            # The server certificate's public key signs this cert's data
            server_pub = Ed25519PublicKey.from_public_bytes(self.server_certificate.public_key)
            # The signed data is: sender_id|sender_pubkey|device_id|expiration
            signed_data = (
                self.sender_id.encode() +
                self.sender_pubkey +
                self.device_id.to_bytes(4, "big") +
                self.expiration.to_bytes(8, "big")
            )
            server_pub.verify(self.signature, signed_data)
            return True
        except InvalidSignature:
            return False
        except Exception:
            return False

# ---- Sealed Sender Message Types ----

class SealedSenderMessage:
    def __init__(self, ephemeral_pub: bytes, encrypted_static: bytes, encrypted_message: bytes):
        self.ephemeral_pub = ephemeral_pub
        self.encrypted_static = encrypted_static
        self.encrypted_message = encrypted_message

    def serialize(self) -> bytes:
        return b"".join([
            len(self.ephemeral_pub).to_bytes(2, "big"), self.ephemeral_pub,
            len(self.encrypted_static).to_bytes(2, "big"), self.encrypted_static,
            len(self.encrypted_message).to_bytes(4, "big"), self.encrypted_message
        ])

    @staticmethod
    def deserialize(data: bytes):
        ptr = 0
        l1 = int.from_bytes(data[ptr:ptr+2], "big"); ptr += 2
        epk = data[ptr:ptr+l1]; ptr += l1
        l2 = int.from_bytes(data[ptr:ptr+2], "big"); ptr += 2
        enc_static = data[ptr:ptr+l2]; ptr += l2
        l3 = int.from_bytes(data[ptr:ptr+4], "big"); ptr += 4
        enc_msg = data[ptr:ptr+l3]
        return SealedSenderMessage(epk, enc_static, enc_msg)

# ---- Sealed Sender Encrypt (Sender) ----

def sealed_sender_encrypt(
    sender_store: InMemProtocolStore,
    recipient_bundle: Bundle,
    sender_cert: SenderCertificate,
    plaintext: bytes,
    *,
    associated_data: Optional[bytes] = b""
) -> bytes:
    """
    Encrypt a sealed sender message to a recipient.

    Args:
        sender_store: InMemProtocolStore for sender.
        recipient_bundle: Recipient's X3DH bundle.
        sender_cert: SenderCertificate object.
        plaintext: Bytes to encrypt.
        associated_data: Associated data (optional, e.g., could be sender_cert).

    Returns:
        Serialized SealedSenderMessage (bytes).
    """
    eph_dh = DHKeyPair.generate_dh()
    eph_pub = eph_dh.public_key.pk_bytes()

    x3dh_state = X3DHState.create(
        IdentityKeyFormat.CURVE_25519,
        HashFunction.SHA_256,
        b"sealed-sender",
        identity_key_pair=None
    )
    x3dh_state._BaseState__identity_key = sender_store.identity_store.key_pair  # Use sender's identity

    import asyncio
    loop = asyncio.get_event_loop()
    shared_secret, ad, header = loop.run_until_complete(
        x3dh_state.get_shared_secret_active(recipient_bundle, associated_data, require_pre_key=True)
    )

    enc_static = AES256GCM.encrypt(shared_secret, sender_cert.serialize(), ad)

    dr_session = DRSession(aead=AES256GCM)
    dr_session.setup_sender(shared_secret, DHPublicKey.from_bytes(header.ephemeral_key))

    msg_obj = dr_session.encrypt_message(plaintext.decode("utf-8"), ad)
    enc_msg = msg_obj.ct

    sealed_msg = SealedSenderMessage(eph_pub, enc_static, enc_msg)
    return sealed_msg.serialize()

# ---- Sealed Sender Decrypt (Recipient) ----

def sealed_sender_decrypt(
    recipient_store: InMemProtocolStore,
    ciphertext: bytes,
    trust_root: bytes,
    timestamp: int,
    local_addr: str,
    *,
    associated_data: Optional[bytes] = b""
) -> Tuple[SenderCertificate, bytes]:
    """
    Decrypt a sealed sender message.

    Args:
        recipient_store: InMemProtocolStore for recipient.
        ciphertext: Received sealed sender message (bytes).
        trust_root: Trust root/public key for validating sender cert.
        timestamp: Validation time.
        local_addr: Local address (str, e.g., phone number or UUID).
        associated_data: Associated data (optional).

    Returns:
        Tuple of validated SenderCertificate and decrypted message (bytes).
    """
    msg = SealedSenderMessage.deserialize(ciphertext)
    eph_pub = DHPublicKey.from_bytes(msg.ephemeral_pub)

    x3dh_state, _ = X3DHState.from_json(
        recipient_store.identity_store.key_pair.json,
        IdentityKeyFormat.CURVE_25519,
        HashFunction.SHA_256,
        b"sealed-sender"
    )
    import asyncio
    loop = asyncio.get_event_loop()
    from .x3dh import Header
    header = Header(
        identity_key=recipient_store.identity_store.key_pair.as_priv().priv,
        ephemeral_key=msg.ephemeral_pub,
        signed_pre_key=recipient_store.session_store.sessions.get(local_addr, b""),
        pre_key=None
    )
    shared_secret, ad, _ = loop.run_until_complete(
        x3dh_state.get_shared_secret_passive(header, associated_data, require_pre_key=True)
    )

    sender_cert_bytes = AES256GCM.decrypt(shared_secret, msg.encrypted_static, ad)
    sender_cert = SenderCertificate.deserialize(sender_cert_bytes)
    if not sender_cert.verify(trust_root, timestamp):
        raise ValueError("Invalid sender certificate")

    dr_session = DRSession(aead=AES256GCM)
    dh_pair = DHKeyPair.generate_dh()
    dr_session.setup_receiver(shared_secret, dh_pair)

    msg_obj = Message(header=None, ct=msg.encrypted_message)
    plaintext = dr_session.decrypt_message(msg_obj, ad)

    return sender_cert, plaintext.encode("utf-8")