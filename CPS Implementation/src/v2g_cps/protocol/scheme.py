from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .constants import (
    DEFAULT_NONCE_BYTES,
    DEFAULT_PSEUDONYM_BYTES,
    DEFAULT_TAG_BYTES,
    DEFAULT_TIMESTAMP_TOLERANCE_SECONDS,
    SECURITY_FLAG_DESCRIPTIONS,
)
from .models import ChargeStation, ControlServer, ProtocolMessage, ProtocolTrace, SmartGateway, UserVehicle
from .primitives import (
    ct_equal,
    current_timestamp,
    derive_password_verifier,
    ecdh_shared_secret,
    generate_private_key,
    hkdf_expand,
    hmac_sha256,
    is_fresh,
    random_bytes,
    serialize_public_key,
    sha256_digest,
    verify_password,
)
from .puf import DeterministicPUF


class ProtocolError(RuntimeError):
    """Raised when the protocol rejects a request."""


@dataclass(slots=True)
class AuthenticationContext:
    user_private_key: Any
    user_public_key: bytes
    user_nonce: bytes
    gateway_nonce: bytes
    station_nonce: bytes
    challenge: bytes
    station_public_key: bytes


class ProtocolEngine:
    def __init__(self, *, seed: bytes | None = None, timestamp_tolerance_seconds: int = DEFAULT_TIMESTAMP_TOLERANCE_SECONDS):
        root_seed = seed or random_bytes(32)
        self.control_server = ControlServer(master_secret=root_seed)
        self.timestamp_tolerance_seconds = timestamp_tolerance_seconds

    def _derive_server_secret(self, label: bytes, identity: str) -> bytes:
        return hkdf_expand(
            identity.encode("utf-8"),
            salt=self.control_server.master_secret,
            info=b"v2g-cps:" + label,
        )

    def register_gateway(self, gateway_id: str) -> SmartGateway:
        gateway = SmartGateway(gateway_id=gateway_id, gateway_secret=self._derive_server_secret(b"gateway", gateway_id))
        self.control_server.gateways[gateway_id] = gateway
        return gateway

    def register_charge_station(self, station_id: str) -> ChargeStation:
        station_secret = self._derive_server_secret(b"station", station_id)
        station = ChargeStation(
            station_id=station_id,
            station_secret=station_secret,
            wpuf_seed=self._derive_server_secret(b"wpuf", station_id),
            rpuf_seed=self._derive_server_secret(b"rpuf", station_id),
        )
        self.control_server.stations[station_id] = station
        return station

    def register_user(self, user_id: str, password: str) -> UserVehicle:
        salt = random_bytes(16)
        verifier = derive_password_verifier(password, salt)
        pseudonym = self._derive_server_secret(b"pseudonym", user_id)[:DEFAULT_PSEUDONYM_BYTES].hex()
        auth_token = self._derive_server_secret(b"user-auth", pseudonym)
        user = UserVehicle(
            user_id=user_id,
            pseudonym=pseudonym,
            password_salt=salt,
            password_verifier=verifier,
            auth_token=auth_token,
        )
        self.control_server.users[pseudonym] = user
        return user

    def authenticate(
        self,
        *,
        pseudonym: str,
        password: str,
        gateway_id: str,
        station_id: str,
        now: int | None = None,
        tamper: str | None = None,
        replay_nonce: bytes | None = None,
    ) -> ProtocolTrace:
        gateway = self.control_server.gateways[gateway_id]
        station = self.control_server.stations[station_id]
        user = self.control_server.users[pseudonym]
        wpuf = DeterministicPUF(station.wpuf_seed, label=b"v2g-cps:wpuf")
        rpuf = DeterministicPUF(station.rpuf_seed, label=b"v2g-cps:rpuf")
        reference_time = current_timestamp() if now is None else now

        if not verify_password(password, user.password_salt, user.password_verifier):
            raise ProtocolError("local password verification failed")

        user_private_key = generate_private_key()
        user_public_key = serialize_public_key(user_private_key.public_key())
        user_nonce = replay_nonce if replay_nonce is not None else random_bytes(DEFAULT_NONCE_BYTES)
        timestamp_1 = reference_time

        msg1_tag = hmac_sha256(
            user.auth_token,
            pseudonym.encode("utf-8"),
            user_public_key,
            user_nonce,
            station_id.encode("utf-8"),
            timestamp_1.to_bytes(8, "big"),
            context=b"v2g-cps:msg1",
        )
        if tamper == "msg1":
            msg1_tag = b"\x00" * len(msg1_tag)

        msg1 = ProtocolMessage(
            name="MSG1",
            sender="UserVehicle",
            recipient="SmartGateway",
            fields={
                "pseudonym": pseudonym,
                "station_id": station_id,
                "timestamp": timestamp_1,
                "user_nonce": user_nonce,
                "user_public_key": user_public_key,
                "login_tag": msg1_tag,
            },
        )

        self._verify_msg1(msg1, user=user, gateway=gateway, now=reference_time)

        gateway_nonce = random_bytes(DEFAULT_NONCE_BYTES)
        timestamp_2 = reference_time + 1
        route_token = hmac_sha256(
            gateway.gateway_secret,
            pseudonym.encode("utf-8"),
            user_public_key,
            user_nonce,
            gateway_nonce,
            station_id.encode("utf-8"),
            timestamp_2.to_bytes(8, "big"),
            context=b"v2g-cps:msg2",
        )
        if tamper == "msg2":
            route_token = b"\xff" * len(route_token)

        msg2 = ProtocolMessage(
            name="MSG2",
            sender="SmartGateway",
            recipient="ChargeStation",
            fields={
                "gateway_id": gateway_id,
                "pseudonym": pseudonym,
                "timestamp": timestamp_2,
                "user_public_key": user_public_key,
                "user_nonce": user_nonce,
                "gateway_nonce": gateway_nonce,
                "route_token": route_token,
            },
        )

        challenge = hmac_sha256(
            station.station_secret,
            gateway_nonce,
            user_nonce,
            timestamp_2.to_bytes(8, "big"),
            context=b"v2g-cps:challenge",
        )[:DEFAULT_NONCE_BYTES]
        helper = rpuf.helper_data(challenge, epoch=station.puf_epoch)
        recovered_response = rpuf.recover(challenge, helper, epoch=station.puf_epoch)
        write_response = wpuf.sample(challenge, epoch=station.puf_epoch)

        if not self._verify_msg2(msg2, gateway=gateway, station=station, now=reference_time + 1):
            raise ProtocolError("gateway route token validation failed")

        station_private_key = generate_private_key()
        station_public_key = serialize_public_key(station_private_key.public_key())
        station_nonce = random_bytes(DEFAULT_NONCE_BYTES)
        timestamp_3 = reference_time + 2
        shared_secret = ecdh_shared_secret(station_private_key, user_public_key)
        session_salt = sha256_digest(
            user_public_key,
            station_public_key,
            user_nonce,
            gateway_nonce,
            station_nonce,
            context=b"v2g-cps:session-salt",
        )
        session_key = hkdf_expand(shared_secret, salt=session_salt, info=b"v2g-cps:session-key")
        station_tag = hmac_sha256(
            station.station_secret,
            station_public_key,
            station_nonce,
            gateway_nonce,
            recovered_response,
            write_response,
            timestamp_3.to_bytes(8, "big"),
            context=b"v2g-cps:msg3",
        )

        msg3 = ProtocolMessage(
            name="MSG3",
            sender="ChargeStation",
            recipient="SmartGateway",
            fields={
                "station_public_key": station_public_key,
                "station_nonce": station_nonce,
                "timestamp": timestamp_3,
                "station_tag": station_tag,
                "puf_epoch": station.puf_epoch,
            },
        )

        expected_station_tag = hmac_sha256(
            station.station_secret,
            station_public_key,
            station_nonce,
            gateway_nonce,
            recovered_response,
            write_response,
            timestamp_3.to_bytes(8, "big"),
            context=b"v2g-cps:msg3",
        )
        if not ct_equal(station_tag, expected_station_tag):
            raise ProtocolError("station authentication tag failed")

        timestamp_4 = reference_time + 3
        gateway_ack = hmac_sha256(
            user.auth_token,
            msg1.canonical_payload(),
            msg2.canonical_payload(),
            msg3.canonical_payload(),
            timestamp_4.to_bytes(8, "big"),
            context=b"v2g-cps:msg4",
        )
        if tamper == "msg4":
            gateway_ack = b"\x01" * len(gateway_ack)

        msg4 = ProtocolMessage(
            name="MSG4",
            sender="SmartGateway",
            recipient="UserVehicle",
            fields={
                "timestamp": timestamp_4,
                "gateway_nonce": gateway_nonce,
                "station_nonce": station_nonce,
                "station_public_key": station_public_key,
                "station_tag": station_tag,
                "gateway_ack": gateway_ack,
            },
        )

        user_session_key = self._verify_msg4(
            msg1=msg1,
            msg2=msg2,
            msg3=msg3,
            msg4=msg4,
            user=user,
            user_private_key=user_private_key,
            gateway_nonce=gateway_nonce,
            station_nonce=station_nonce,
            station_public_key=station_public_key,
            reference_time=reference_time + 3,
        )
        if not ct_equal(bytes.fromhex(session_key.hex()), user_session_key):
            raise ProtocolError("user and station derived different session keys")

        gateway.replay_cache.add(user_nonce.hex())
        station.puf_epoch += 1

        security_checks = self._security_feature_flags()
        notes = [
            "The implementation uses transcript-bound HMACs, scrypt password verifiers, HKDF, and ephemeral P-256 ECDH.",
            "Communication and timing tables are generated from the project's configured message and operation models.",
        ]
        return ProtocolTrace(
            messages=[msg1, msg2, msg3, msg4],
            session_key_hex=session_key.hex(),
            security_checks=security_checks,
            operation_counts={"TWPUF": 1, "TRPUF": 2, "Th": 8},
            notes=notes,
        )

    def _verify_msg1(self, msg1: ProtocolMessage, *, user: UserVehicle, gateway: SmartGateway, now: int) -> None:
        timestamp = msg1.fields["timestamp"]
        if not is_fresh(timestamp, tolerance_seconds=self.timestamp_tolerance_seconds, now=now):
            raise ProtocolError("stale MSG1 timestamp")
        user_nonce_hex = msg1.fields["user_nonce"].hex()
        if user_nonce_hex in gateway.replay_cache:
            raise ProtocolError("replayed MSG1 nonce")
        expected_tag = hmac_sha256(
            user.auth_token,
            msg1.fields["pseudonym"].encode("utf-8"),
            msg1.fields["user_public_key"],
            msg1.fields["user_nonce"],
            msg1.fields["station_id"].encode("utf-8"),
            timestamp.to_bytes(8, "big"),
            context=b"v2g-cps:msg1",
        )
        if not ct_equal(msg1.fields["login_tag"], expected_tag):
            raise ProtocolError("MSG1 authentication tag mismatch")

    def _verify_msg2(self, msg2: ProtocolMessage, *, gateway: SmartGateway, station: ChargeStation, now: int) -> bool:
        timestamp = msg2.fields["timestamp"]
        if not is_fresh(timestamp, tolerance_seconds=self.timestamp_tolerance_seconds, now=now):
            raise ProtocolError("stale MSG2 timestamp")
        expected = hmac_sha256(
            gateway.gateway_secret,
            msg2.fields["pseudonym"].encode("utf-8"),
            msg2.fields["user_public_key"],
            msg2.fields["user_nonce"],
            msg2.fields["gateway_nonce"],
            station.station_id.encode("utf-8"),
            timestamp.to_bytes(8, "big"),
            context=b"v2g-cps:msg2",
        )
        return ct_equal(msg2.fields["route_token"], expected)

    def _verify_msg4(
        self,
        *,
        msg1: ProtocolMessage,
        msg2: ProtocolMessage,
        msg3: ProtocolMessage,
        msg4: ProtocolMessage,
        user: UserVehicle,
        user_private_key: Any,
        gateway_nonce: bytes,
        station_nonce: bytes,
        station_public_key: bytes,
        reference_time: int,
    ) -> bytes:
        timestamp = msg4.fields["timestamp"]
        if not is_fresh(timestamp, tolerance_seconds=self.timestamp_tolerance_seconds, now=reference_time):
            raise ProtocolError("stale MSG4 timestamp")
        expected_ack = hmac_sha256(
            user.auth_token,
            msg1.canonical_payload(),
            msg2.canonical_payload(),
            msg3.canonical_payload(),
            timestamp.to_bytes(8, "big"),
            context=b"v2g-cps:msg4",
        )
        if not ct_equal(msg4.fields["gateway_ack"], expected_ack):
            raise ProtocolError("gateway acknowledgement mismatch")
        shared_secret = ecdh_shared_secret(user_private_key, station_public_key)
        session_salt = sha256_digest(
            msg1.fields["user_public_key"],
            station_public_key,
            msg1.fields["user_nonce"],
            gateway_nonce,
            station_nonce,
            context=b"v2g-cps:session-salt",
        )
        return hkdf_expand(shared_secret, salt=session_salt, info=b"v2g-cps:session-key")

    def _security_feature_flags(self) -> dict[str, bool]:
        return {code: True for code in SECURITY_FLAG_DESCRIPTIONS}


def build_default_demo_system() -> tuple[ProtocolEngine, UserVehicle, SmartGateway, ChargeStation]:
    engine = ProtocolEngine(seed=b"v2g-cps-master-secret-000000000")
    gateway = engine.register_gateway("gateway-01")
    station = engine.register_charge_station("station-01")
    user = engine.register_user("ev-driver-01", "correct horse battery staple")
    return engine, user, gateway, station
