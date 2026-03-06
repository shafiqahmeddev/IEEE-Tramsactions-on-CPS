from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from typing import Any


def _json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"base64": base64.b64encode(value).decode("ascii")}
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


@dataclass(slots=True)
class DeviceProfile:
    name: str
    operation_cost_ms: dict[str, float]


@dataclass(slots=True)
class ProtocolMessage:
    name: str
    sender: str
    recipient: str
    fields: dict[str, Any]

    def canonical_payload(self) -> bytes:
        payload = {
            "fields": _json_safe(self.fields),
            "name": self.name,
            "recipient": self.recipient,
            "sender": self.sender,
        }
        return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    @property
    def derived_bits(self) -> int:
        return len(self.canonical_payload()) * 8

    def to_dict(self) -> dict[str, Any]:
        return {
            "derived_bits": self.derived_bits,
            "fields": _json_safe(self.fields),
            "name": self.name,
            "recipient": self.recipient,
            "sender": self.sender,
        }


@dataclass(slots=True)
class ProtocolTrace:
    messages: list[ProtocolMessage]
    session_key_hex: str
    security_checks: dict[str, bool]
    operation_counts: dict[str, int]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "notes": self.notes,
            "message_count": len(self.messages),
            "messages": [message.to_dict() for message in self.messages],
            "operation_counts": self.operation_counts,
            "security_checks": self.security_checks,
            "session_key_hex": self.session_key_hex,
        }


@dataclass(slots=True)
class UserVehicle:
    user_id: str
    pseudonym: str
    password_salt: bytes
    password_verifier: bytes
    auth_token: bytes


@dataclass(slots=True)
class SmartGateway:
    gateway_id: str
    gateway_secret: bytes
    replay_cache: set[str] = field(default_factory=set)


@dataclass(slots=True)
class ChargeStation:
    station_id: str
    station_secret: bytes
    wpuf_seed: bytes
    rpuf_seed: bytes
    puf_epoch: int = 0


@dataclass(slots=True)
class ControlServer:
    master_secret: bytes
    users: dict[str, UserVehicle] = field(default_factory=dict)
    gateways: dict[str, SmartGateway] = field(default_factory=dict)
    stations: dict[str, ChargeStation] = field(default_factory=dict)

