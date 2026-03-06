from __future__ import annotations

import argparse
from pathlib import Path

from v2g_cps.common import DATA_ROOT, MODELS_ROOT, REPORTS_ROOT, RESULTS_ROOT, TRACES_ROOT, ensure_output_directories, write_json
from v2g_cps.ml.train import run_training_pipeline
from v2g_cps.protocol.costs import benchmark_local_operation_costs, build_paper_device_profiles
from v2g_cps.protocol.scheme import build_default_demo_system
from v2g_cps.analysis.report import write_implementation_report
from v2g_cps.analysis.tables import build_table_iii, build_table_iv, build_table_v, write_csv


def run_pipeline(*, dataset_root: Path, max_samples: int, epochs: int, batch_size: int) -> dict[str, str]:
    ensure_output_directories()
    engine, user, gateway, station = build_default_demo_system()
    trace = engine.authenticate(
        pseudonym=user.pseudonym,
        password="correct horse battery staple",
        gateway_id=gateway.gateway_id,
        station_id=station.station_id,
    )
    trace_path = TRACES_ROOT / "protocol_trace.json"
    write_json(trace_path, trace.to_dict())

    paper_user_profile, paper_esp_profile = build_paper_device_profiles()
    local_costs = benchmark_local_operation_costs()
    table_iii = build_table_iii(trace)
    table_iv = build_table_iv(paper_user_profile=paper_user_profile, local_operation_costs=local_costs)
    table_v = build_table_v(local_costs, user_profile=paper_user_profile, esp_profile=paper_esp_profile)

    table_iii_path = RESULTS_ROOT / "table_iii.csv"
    table_iv_path = RESULTS_ROOT / "table_iv.csv"
    table_v_path = RESULTS_ROOT / "table_v.csv"
    write_csv(table_iii, table_iii_path)
    write_csv(table_iv, table_iv_path)
    write_csv(table_v, table_v_path)

    ml_output_root = MODELS_ROOT / "kdd"
    ml_metrics = run_training_pipeline(
        dataset_root=dataset_root,
        output_root=ml_output_root,
        max_samples=max_samples,
        epochs=epochs,
        batch_size=batch_size,
    )

    report_path = REPORTS_ROOT / "implementation_report.md"
    write_implementation_report(
        output_path=report_path,
        trace=trace,
        ml_metrics=ml_metrics,
        table_iii=table_iii,
        table_iv=table_iv,
        table_v=table_v,
    )

    return {
        "report": str(report_path),
        "table_iii": str(table_iii_path),
        "table_iv": str(table_iv_path),
        "table_v": str(table_v_path),
        "trace": str(trace_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the end-to-end V2G CPS implementation pipeline.")
    parser.add_argument("--dataset-root", type=Path, default=DATA_ROOT / "raw" / "kddcup99")
    parser.add_argument("--max-samples", type=int, default=10000)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=128)
    args = parser.parse_args()

    outputs = run_pipeline(
        dataset_root=args.dataset_root,
        max_samples=args.max_samples,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )
    print(outputs)


if __name__ == "__main__":
    main()
