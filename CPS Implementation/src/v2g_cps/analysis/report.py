from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from v2g_cps.protocol.constants import PAPER_SECURITY_FEATURES
from v2g_cps.protocol.models import ProtocolTrace


def _markdown_table(df: pd.DataFrame) -> str:
    columns = list(df.columns)
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for record in df.to_dict(orient="records"):
        rows.append("| " + " | ".join(str(record[column]) for column in columns) + " |")
    return "\n".join([header, separator, *rows])


def _bullet_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def write_implementation_report(
    *,
    output_path: Path,
    trace: ProtocolTrace,
    ml_metrics: dict[str, object],
    table_iii: pd.DataFrame,
    table_iv: pd.DataFrame,
    table_v: pd.DataFrame,
) -> None:
    security_feature_map = ", ".join(f"{code}={label}" for code, label in PAPER_SECURITY_FEATURES)
    report = f"""# Implementation Report

## Summary
- This project provides a Python implementation of the article's secure V2G protocol and anomaly-detection workflow.
- The protocol flow completed successfully and produced a session key.
- The tables below summarize the current implementation outputs and reference values used by the project.

## Protocol Run
- Session key: `{trace.session_key_hex}`
- Message count: {len(trace.messages)}
- Security feature codes: {security_feature_map}

### Implementation Notes
{_bullet_list(trace.notes)}

## Table III
{_markdown_table(table_iii)}

## Table IV
{_markdown_table(table_iv.fillna('n/a'))}

## Table V
{_markdown_table(table_v.fillna('n/a'))}

## ML Metrics
### Dataset
{_bullet_list(f"{key}: {value}" for key, value in ml_metrics["dataset"].items())}

### LSTM
{_bullet_list(f"{key}: {value}" for key, value in ml_metrics["lstm"].items())}

### MLP Baseline
{_bullet_list(f"{key}: {value}" for key, value in ml_metrics["mlp"].items())}
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
