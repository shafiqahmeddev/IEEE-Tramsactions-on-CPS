from __future__ import annotations

from pathlib import Path

import pandas as pd

from v2g_cps.protocol.constants import (
    PAPER_SECURITY_FEATURES,
    PAPER_TABLE_III_ROWS,
    PAPER_TABLE_IV_ROWS,
)
from v2g_cps.protocol.costs import compute_formula_ms
from v2g_cps.protocol.models import DeviceProfile, ProtocolTrace


def build_table_iii(trace: ProtocolTrace) -> pd.DataFrame:
    rows = [row.copy() for row in PAPER_TABLE_III_ROWS]
    proposed = {"protocol": "Proposed"}
    proposed.update({feature: "Y" if trace.security_checks[feature] else "N" for feature, _ in PAPER_SECURITY_FEATURES})
    rows.append(proposed)
    return pd.DataFrame(rows)


def build_table_iv(
    *,
    paper_user_profile: DeviceProfile,
    local_operation_costs: dict[str, float],
) -> pd.DataFrame:
    rows = []
    for row in PAPER_TABLE_IV_ROWS:
        recomputed_user_ms = compute_formula_ms(row["operation_counts"], paper_user_profile)
        local_recomputed_ms = compute_formula_ms(row["operation_counts"], local_operation_costs)
        rows.append(
            {
                "reference": row["reference"],
                "formula": row["formula"],
                "paper_reported_ms": row["reported_ms"],
                "paper_formula_ms_from_table_v_user": recomputed_user_ms,
                "local_formula_ms": local_recomputed_ms,
                "paper_reported_communication_bytes": row["reported_communication_bytes"],
            }
        )
    return pd.DataFrame(rows)


def build_table_v(local_operation_costs: dict[str, float], *, user_profile: DeviceProfile, esp_profile: DeviceProfile) -> pd.DataFrame:
    rows = []
    for operation, paper_user_ms in user_profile.operation_cost_ms.items():
        rows.append(
            {
                "operation": operation,
                "paper_user_device_ms": paper_user_ms,
                "paper_esp_cs_ms": esp_profile.operation_cost_ms[operation],
                "local_ms": local_operation_costs.get(operation),
            }
        )
    return pd.DataFrame(rows)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
