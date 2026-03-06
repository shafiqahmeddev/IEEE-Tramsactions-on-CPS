from __future__ import annotations

from dataclasses import dataclass

from .constants import DEFAULT_RESPONSE_BYTES
from .primitives import ct_equal, hmac_sha256, sha256_digest


def _flip_bits(source: bytes, mask: bytes) -> bytes:
    return bytes(left ^ right for left, right in zip(source, mask, strict=True))


@dataclass(slots=True)
class DeterministicPUF:
    seed: bytes
    label: bytes
    response_bytes: int = DEFAULT_RESPONSE_BYTES
    noise_mask_bytes: int = DEFAULT_RESPONSE_BYTES

    def base_response(self, challenge: bytes, *, epoch: int = 0) -> bytes:
        epoch_bytes = epoch.to_bytes(4, "big")
        return hmac_sha256(self.seed, challenge, epoch_bytes, context=self.label)[: self.response_bytes]

    def helper_data(self, challenge: bytes, *, epoch: int = 0) -> bytes:
        response = self.base_response(challenge, epoch=epoch)
        return hmac_sha256(self.seed, challenge, response, context=self.label + b":helper")

    def sample(self, challenge: bytes, *, epoch: int = 0, noisy: bool = False) -> bytes:
        response = self.base_response(challenge, epoch=epoch)
        if not noisy:
            return response
        noise_mask = sha256_digest(self.seed, challenge, epoch.to_bytes(4, "big"), context=self.label + b":noise")[
            : self.noise_mask_bytes
        ]
        return _flip_bits(response, noise_mask)

    def recover(self, challenge: bytes, helper: bytes, *, epoch: int = 0) -> bytes:
        expected_helper = self.helper_data(challenge, epoch=epoch)
        if not ct_equal(helper, expected_helper):
            raise ValueError("helper data mismatch")
        return self.base_response(challenge, epoch=epoch)

