from v2g_cps.protocol.costs import build_paper_device_profiles
from v2g_cps.protocol.scheme import build_default_demo_system
from v2g_cps.analysis.tables import build_table_iv


def test_table_iv_includes_proposed_row() -> None:
    engine, user, gateway, station = build_default_demo_system()
    engine.authenticate(
        pseudonym=user.pseudonym,
        password="correct horse battery staple",
        gateway_id=gateway.gateway_id,
        station_id=station.station_id,
    )
    paper_user_profile, _ = build_paper_device_profiles()
    table = build_table_iv(paper_user_profile=paper_user_profile, local_operation_costs=paper_user_profile.operation_cost_ms)
    proposed_row = table[table["reference"] == "Proposed"].iloc[0]
    assert proposed_row["paper_formula_ms_from_table_v_user"] == 9.0118
    assert proposed_row["paper_reported_communication_bytes"] == 216
