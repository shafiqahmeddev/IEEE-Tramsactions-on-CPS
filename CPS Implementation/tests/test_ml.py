from pathlib import Path

import numpy as np
import pandas as pd

from v2g_cps.ml.data import KDD_FEATURES
from v2g_cps.ml.train import run_training_pipeline


def test_training_pipeline_runs_with_synthetic_data(tmp_path: Path, monkeypatch) -> None:
    rows = 240
    rng = np.random.default_rng(7)
    data = pd.DataFrame(rng.normal(size=(rows, len(KDD_FEATURES))), columns=KDD_FEATURES)
    data["label"] = ["normal" if index % 3 else "attack" for index in range(rows)]

    def fake_loader(dataset_root: Path) -> pd.DataFrame:
        return data.copy()

    monkeypatch.setattr("v2g_cps.ml.train.load_or_fetch_kddcup99", fake_loader)

    metrics = run_training_pipeline(
        dataset_root=tmp_path / "dataset",
        output_root=tmp_path / "models",
        max_samples=180,
        epochs=1,
        batch_size=32,
        seq_len=5,
    )
    assert "lstm" in metrics
    assert "mlp" in metrics
    assert (tmp_path / "models" / "metrics.json").exists()
    assert (tmp_path / "models" / "lstm.pt").exists()
