#!/usr/bin/env python3
# ──────────────────────────────
#   Eclyptic ECC         v1.2.0
#   Author      jts.gg/eclyptic
#   License   r2.jts.gg/license
# ──────────────────────────────

import os
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ────── base64 helper functions ──────
def b64u_nopad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def b64u_nopad_decode(s: str) -> bytes:
    padding = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + padding)

# ────── generate ECC keypair ──────
def keypair(curve_name: str = "secp256r1") -> tuple[str, str]:
    curve_cls = getattr(ec, curve_name.upper(), ec.SECP256R1)
    priv_obj = ec.generate_private_key(curve_cls())

    # private scalar → fixed-length bytes
    priv_int = priv_obj.private_numbers().private_value
    priv_bytes = priv_int.to_bytes(curve_cls().key_size // 8, "big")
    priv_b64 = b64u_nopad(priv_bytes)

    # compressed public point → bytes
    pub_bytes = priv_obj.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.CompressedPoint
    )
    pub_b64 = b64u_nopad(pub_bytes)

    return priv_b64, pub_b64

# ────── ECIES-style encryption ──────
def encrypt(pub_b64: str, plaintext: bytes | str) -> bytes:
    curve = ec.SECP256R1()
    raw_pub = b64u_nopad_decode(pub_b64)
    pub_obj = ec.EllipticCurvePublicKey.from_encoded_point(curve, raw_pub)

    data = plaintext.encode() if isinstance(plaintext, str) else plaintext

    eph_priv = ec.generate_private_key(curve)
    shared = eph_priv.exchange(ec.ECDH(), pub_obj)

    sym_key = HKDF(algorithm=hashes.SHA256(), length=32,
                   salt=None, info=b"ecies").derive(shared)

    aesgcm = AESGCM(sym_key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, data, None)

    eph_pub = eph_priv.public_key().public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.CompressedPoint
    )
    return len(eph_pub).to_bytes(2, "big") + eph_pub + nonce + ct

# ────── ECIES-style decryption ──────
def decrypt(priv_b64: str, ciphertext: bytes) -> bytes:
    curve = ec.SECP256R1()

    priv_bytes = b64u_nopad_decode(priv_b64)
    priv_int = int.from_bytes(priv_bytes, "big")
    priv_obj = ec.derive_private_key(priv_int, curve)

    eplen = int.from_bytes(ciphertext[:2], "big")
    offset = 2
    eph_bytes = ciphertext[offset : offset + eplen];  offset += eplen
    nonce     = ciphertext[offset : offset + 12];      offset += 12
    ct        = ciphertext[offset:]

    eph_pub = ec.EllipticCurvePublicKey.from_encoded_point(curve, eph_bytes)
    shared  = priv_obj.exchange(ec.ECDH(), eph_pub)

    sym_key = HKDF(algorithm=hashes.SHA256(), length=32,
                   salt=None, info=b"ecies").derive(shared)

    return AESGCM(sym_key).decrypt(nonce, ct, None)