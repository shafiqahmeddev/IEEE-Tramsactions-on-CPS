from __future__ import annotations

import statistics
import time
from typing import Callable

from .constants import PAPER_OPERATION_ORDER, PAPER_TABLE_V_ESP_CS, PAPER_TABLE_V_USER_DEVICE
from .models import DeviceProfile
from .primitives import (
    aes_gcm_encrypt,
    ecdh_shared_secret,
    generate_private_key,
    serialize_public_key,
    sha256_digest,
)
from .puf import DeterministicPUF


def build_paper_device_profiles() -> tuple[DeviceProfile, DeviceProfile]:
    return (
        DeviceProfile(name="Paper User Device", operation_cost_ms=PAPER_TABLE_V_USER_DEVICE.copy()),
        DeviceProfile(name="Paper ESP/CS", operation_cost_ms=PAPER_TABLE_V_ESP_CS.copy()),
    )


def compute_formula_ms(operation_counts: dict[str, int], profile: DeviceProfile | dict[str, float]) -> float | None:
    costs = profile.operation_cost_ms if isinstance(profile, DeviceProfile) else profile
    total = 0.0
    for operation, count in operation_counts.items():
        if operation not in costs:
            return None
        total += costs[operation] * count
    return round(total, 4)


def _benchmark(label: str, fn: Callable[[], object], rounds: int, warmup: int = 5) -> tuple[str, float]:
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(rounds):
        start = time.perf_counter()
        fn()
        elapsed_ms = (time.perf_counter() - start) * 1000
        samples.append(elapsed_ms)
    return label, round(statistics.mean(samples), 6)


def benchmark_local_operation_costs(rounds: int = 40) -> dict[str, float]:
    hash_payload = b"A" * 64
    aes_key = sha256_digest(b"aes-key", context=b"v2g-cps:aes-key")[:16]
    aes_payload = b"vehicle-to-grid" * 8
    station_priv = generate_private_key()
    peer_priv = generate_private_key()
    peer_pub_bytes = serialize_public_key(peer_priv.public_key())
    wpuf = DeterministicPUF(seed=b"wpuf-seed" * 4, label=b"v2g-cps:wpuf")
    rpuf = DeterministicPUF(seed=b"rpuf-seed" * 4, label=b"v2g-cps:rpuf")
    challenge = b"benchmark-challenge"
    helper = rpuf.helper_data(challenge)
    base = int.from_bytes(sha256_digest(b"base", context=b"v2g-cps:modexp"), "big")
    exponent = int.from_bytes(sha256_digest(b"exponent", context=b"v2g-cps:modexp"), "big")
    modulus = (1 << 2048) - 159

    benchmarks = dict(
        [
            _benchmark("Th", lambda: sha256_digest(hash_payload, context=b"v2g-cps:hash-bench"), rounds=rounds * 4),
            _benchmark("Tm", lambda: pow(base, exponent, modulus), rounds=rounds),
            _benchmark("Tpm", lambda: ecdh_shared_secret(station_priv, peer_pub_bytes), rounds=rounds),
            _benchmark("TSenc", lambda: aes_gcm_encrypt(aes_key, aes_payload, b"bench"), rounds=rounds * 2),
            _benchmark("TPUF", lambda: wpuf.sample(challenge, epoch=0), rounds=rounds * 4),
            _benchmark("TWPUF", lambda: wpuf.sample(challenge, epoch=1), rounds=rounds * 4),
            _benchmark("TRPUF", lambda: rpuf.recover(challenge, helper, epoch=0), rounds=rounds * 4),
        ]
    )
    return benchmarks


def build_paper_table_v_rows(local_operation_costs: dict[str, float]) -> list[dict[str, float | str | None]]:
    rows: list[dict[str, float | str | None]] = []
    for operation in PAPER_OPERATION_ORDER:
        rows.append(
            {
                "operation": operation,
                "paper_user_device_ms": PAPER_TABLE_V_USER_DEVICE[operation],
                "paper_esp_cs_ms": PAPER_TABLE_V_ESP_CS[operation],
                "local_ms": local_operation_costs.get(operation),
            }
        )
    return rows
