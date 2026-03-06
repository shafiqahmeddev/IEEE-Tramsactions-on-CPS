import pytest

from v2g_cps.protocol.scheme import ProtocolError, build_default_demo_system


def test_protocol_happy_path() -> None:
    engine, user, gateway, station = build_default_demo_system()
    trace = engine.authenticate(
        pseudonym=user.pseudonym,
        password="correct horse battery staple",
        gateway_id=gateway.gateway_id,
        station_id=station.station_id,
    )
    assert len(trace.messages) == 4
    assert len(trace.session_key_hex) == 64
    assert all(trace.security_checks.values())


def test_protocol_rejects_tampered_message() -> None:
    engine, user, gateway, station = build_default_demo_system()
    with pytest.raises(ProtocolError):
        engine.authenticate(
            pseudonym=user.pseudonym,
            password="correct horse battery staple",
            gateway_id=gateway.gateway_id,
            station_id=station.station_id,
            tamper="msg4",
        )


def test_protocol_rejects_replay_nonce() -> None:
    engine, user, gateway, station = build_default_demo_system()
    fixed_nonce = b"\xAA" * 16
    engine.authenticate(
        pseudonym=user.pseudonym,
        password="correct horse battery staple",
        gateway_id=gateway.gateway_id,
        station_id=station.station_id,
        replay_nonce=fixed_nonce,
    )
    with pytest.raises(ProtocolError):
        engine.authenticate(
            pseudonym=user.pseudonym,
            password="correct horse battery staple",
            gateway_id=gateway.gateway_id,
            station_id=station.station_id,
            replay_nonce=fixed_nonce,
        )

