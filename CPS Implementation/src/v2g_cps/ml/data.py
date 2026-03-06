from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.datasets import fetch_kddcup99
from sklearn.model_selection import train_test_split

KDD_FEATURES = [
    "src_bytes",
    "dst_bytes",
    "hot",
    "logged_in",
    "num_compromised",
    "num_root",
    "num_file_creations",
    "num_shells",
    "count",
    "srv_count",
    "dst_host_same_src_port_rate",
]


def _decode_target(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def load_or_fetch_kddcup99(dataset_root: Path) -> pd.DataFrame:
    dataset_root.mkdir(parents=True, exist_ok=True)
    cached_path = dataset_root / "kddcup99_selected.csv"
    if cached_path.exists():
        return pd.read_csv(cached_path)

    bunch = fetch_kddcup99(percent10=True, shuffle=False, as_frame=True)
    frame = bunch.data.copy()
    frame["label"] = bunch.target.map(_decode_target)
    frame["label"] = frame["label"].apply(lambda value: "normal" if value == "normal." else "attack")
    selected = frame[KDD_FEATURES + ["label"]].copy()
    selected.to_csv(cached_path, index=False)
    return selected


def sample_dataset(frame: pd.DataFrame, *, max_samples: int | None, seed: int) -> pd.DataFrame:
    if max_samples is None or max_samples <= 0 or len(frame) <= max_samples:
        return frame.copy()

    sampled, _ = train_test_split(
        frame,
        train_size=max_samples,
        stratify=frame["label"],
        random_state=seed,
    )
    return sampled.sort_index().reset_index(drop=True)
