from __future__ import annotations

import hashlib
import hmac
import time
from secrets import token_bytes

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes, hmac as crypto_hmac, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def random_bytes(length: int) -> bytes:
    return token_bytes(length)


def sha256_digest(*parts: bytes, context: bytes = b"v2g-cps:hash") -> bytes:
    digest = hashlib.sha256()
    digest.update(context)
    for part in parts:
        digest.update(part)
    return digest.digest()


def hmac_sha256(key: bytes, *parts: bytes, context: bytes) -> bytes:
    signer = crypto_hmac.HMAC(key, hashes.SHA256())
    signer.update(context)
    for part in parts:
        signer.update(part)
    return signer.finalize()


def ct_equal(left: bytes, right: bytes) -> bool:
    return hmac.compare_digest(left, right)


def derive_password_verifier(password: str, salt: bytes, length: int = 32) -> bytes:
    kdf = Scrypt(salt=salt, length=length, n=2**14, r=8, p=1)
    return kdf.derive(password.encode("utf-8"))


def verify_password(password: str, salt: bytes, verifier: bytes) -> bool:
    kdf = Scrypt(salt=salt, length=len(verifier), n=2**14, r=8, p=1)
    try:
        kdf.verify(password.encode("utf-8"), verifier)
    except InvalidKey:
        return False
    return True


def hkdf_expand(ikm: bytes, *, salt: bytes, info: bytes, length: int = 32) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=length, salt=salt, info=info).derive(ikm)


def generate_private_key() -> ec.EllipticCurvePrivateKey:
    return ec.generate_private_key(ec.SECP256R1())


def serialize_public_key(public_key: ec.EllipticCurvePublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.CompressedPoint,
    )


def load_public_key(encoded: bytes) -> ec.EllipticCurvePublicKey:
    return ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), encoded)


def ecdh_shared_secret(private_key: ec.EllipticCurvePrivateKey, peer_public_key_bytes: bytes) -> bytes:
    peer_public_key = load_public_key(peer_public_key_bytes)
    return private_key.exchange(ec.ECDH(), peer_public_key)


def current_timestamp() -> int:
    return int(time.time())


def is_fresh(timestamp: int, *, tolerance_seconds: int, now: int | None = None) -> bool:
    reference = current_timestamp() if now is None else now
    return abs(reference - timestamp) <= tolerance_seconds


def aes_gcm_encrypt(key: bytes, plaintext: bytes, aad: bytes = b"") -> tuple[bytes, bytes]:
    nonce = random_bytes(12)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad)
    return nonce, ciphertext

