"""
Signal-style group message encryption/decryption for Discord bot group chats.

- Uses sender_keys.py logic for SenderKeyRecord/State/ChainKey/MessageKey.
- Each group has a single SenderKeyRecord per participant.
- Each bot holds their own SenderKeyRecord and shares SenderKeyDistributionMessage on join.

You need to implement message distribution (send/receive) logic outside of this file.

Dependencies:
    - sender_keys.py (from airjam)
    - cryptography/hmac/sha256 for key derivation
"""

import os
import secrets
from typing import Dict, Optional, List

from .sender_keys import (
    SenderKeyRecord, SenderKeyState, SenderChainKey, SenderMessageKey, _hmac_sha256
)

# -- Utility for group key id --
def random_sender_key_id() -> int:
    return secrets.randbelow(2**31)

def random_bytes(n: int) -> bytes:
    return os.urandom(n)

# -- Sender key distribution message (serialize the state for others) --
def create_sender_key_distribution_message(state: SenderKeyState) -> bytes:
    """
    Create the message to share a new SenderKeyState with the group.
    """
    from sender_key_pb2 import textsecure__SenderKeyDistributionMessage
    msg = textsecure__SenderKeyDistributionMessage()
    msg.id = state.sender_key_id
    msg.iteration = state.sender_chain_key.iteration
    msg.chainKey = state.sender_chain_key.chain_key
    msg.signingKey = state.sender_signing_pub
    return msg.SerializeToString()

def parse_sender_key_distribution_message(data: bytes) -> SenderKeyState:
    from sender_key_pb2 import textsecure__SenderKeyDistributionMessage
    msg = textsecure__SenderKeyDistributionMessage()
    msg.ParseFromString(data)
    chain_key = SenderChainKey(msg.iteration, msg.chainKey)
    return SenderKeyState(
        sender_key_id=msg.id,
        sender_chain_key=chain_key,
        sender_signing_pub=msg.signingKey,
        sender_signing_priv=None
    )

# -- Group encryption/decryption logic --
class GroupCipher:
    """
    One instance per group per user.
    """
    def __init__(self, group_id: str, sender_key_store):
        self.group_id = group_id
        self.store = sender_key_store  # InMemSenderKeyStore

    def _get_record(self) -> SenderKeyRecord:
        rec_bytes = self.store.load_sender_key(self.group_id)
        if rec_bytes:
            return SenderKeyRecord.deserialize(rec_bytes)
        else:
            rec = SenderKeyRecord.new_empty()
            self.store.store_sender_key(self.group_id, rec.serialize())
            return rec

    def _set_record(self, rec: SenderKeyRecord):
        self.store.store_sender_key(self.group_id, rec.serialize())

    def create_state(self, pub_signing: bytes, priv_signing: bytes) -> SenderKeyState:
        chain_key = SenderChainKey(0, random_bytes(32))
        sender_key_id = random_sender_key_id()
        state = SenderKeyState(
            sender_key_id=sender_key_id,
            sender_chain_key=chain_key,
            sender_signing_pub=pub_signing,
            sender_signing_priv=priv_signing
        )
        rec = self._get_record()
        rec.set_sender_key_state(state)
        self._set_record(rec)
        return state

    def process_sender_key_distribution_message(self, data: bytes):
        new_state = parse_sender_key_distribution_message(data)
        rec = self._get_record()
        rec.add_sender_key_state(new_state)
        self._set_record(rec)

    def encrypt(self, plaintext: bytes) -> bytes:
        rec = self._get_record()
        if rec.is_empty():
            raise Exception("No sender key state available for this group")
        state = rec.states[0]
        chain_key = state.sender_chain_key
        msg_key = chain_key.sender_message_key()
        # Simple symmetric encryption using msg_key.seed as key (use e.g. ChaCha20Poly1305 or AES-GCM)
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        nonce = random_bytes(12)
        cipher = ChaCha20Poly1305(msg_key.seed)
        ciphertext = cipher.encrypt(nonce, plaintext, None)
        # Track the used message key
        state.add_sender_message_key(msg_key)
        state.sender_chain_key = chain_key.next()
        rec.states[0] = state
        self._set_record(rec)
        return msg_key.iteration.to_bytes(4, "big") + nonce + ciphertext

    def decrypt(self, data: bytes) -> bytes:
        rec = self._get_record()
        if rec.is_empty():
            raise Exception("No sender key state available for this group")
        state = rec.states[0]
        iter_num = int.from_bytes(data[:4], "big")
        nonce = data[4:16]
        ciphertext = data[16:]
        # Try to find or derive the message key
        mk = None
        if state.has_sender_message_key(iter_num):
            mk = state.remove_sender_message_key(iter_num)
        else:
            # Derive forward (skip message keys for forward secrecy)
            ck = state.sender_chain_key
            for _ in range(iter_num - ck.iteration):
                ck = ck.next()
            mk = ck.sender_message_key()
            # Update state to reflect chain key progress
            state.sender_chain_key = ck.next()
        # Decrypt
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        cipher = ChaCha20Poly1305(mk.seed)
        plaintext = cipher.decrypt(nonce, ciphertext, None)
        rec.states[0] = state
        self._set_record(rec)
        return plaintext

# --- Example usage in Discord bot context ---

# 1. Each bot generates its own signing keypair (ed25519) externally.
# 2. Call create_state() on GroupCipher to initialize and produce distribution message.
# 3. Share the distribution message with the other bots.
# 4. Each bot calls process_sender_key_distribution_message() to accept others' keys.
# 5. Use encrypt() to send, decrypt() to receive.

# NOTE: You are responsible for synchronizing SenderKeyDistributionMessage to all group members.