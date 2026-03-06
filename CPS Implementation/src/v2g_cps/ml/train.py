from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from v2g_cps.common import ensure_output_directories, seed_everything, write_json
from v2g_cps.ml.data import KDD_FEATURES, load_or_fetch_kddcup99, sample_dataset
from v2g_cps.ml.models import MLPBaseline, LSTMClassifier, TrainingBundle, build_loader, evaluate_binary_model, train_binary_model


def _to_binary(series: pd.Series) -> np.ndarray:
    return series.map({"normal": 0, "attack": 1}).astype(int).to_numpy()


def _make_sequences(features: np.ndarray, labels: np.ndarray, seq_len: int) -> tuple[np.ndarray, np.ndarray]:
    windows = []
    window_labels = []
    for index in range(seq_len - 1, len(features)):
        windows.append(features[index - seq_len + 1 : index + 1])
        window_labels.append(labels[index])
    return np.asarray(windows, dtype=np.float32), np.asarray(window_labels, dtype=np.int64)


def _split_frame(frame: pd.DataFrame, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_frame, temp_frame = train_test_split(frame, test_size=0.3, stratify=frame["label"], random_state=seed)
    val_frame, test_frame = train_test_split(temp_frame, test_size=0.5, stratify=temp_frame["label"], random_state=seed)
    return (
        train_frame.sort_index().reset_index(drop=True),
        val_frame.sort_index().reset_index(drop=True),
        test_frame.sort_index().reset_index(drop=True),
    )


def run_training_pipeline(
    *,
    dataset_root: Path,
    output_root: Path,
    seed: int = 7,
    max_samples: int = 10000,
    seq_len: int = 10,
    epochs: int = 3,
    batch_size: int = 128,
) -> dict[str, object]:
    seed_everything(seed)
    output_root.mkdir(parents=True, exist_ok=True)

    frame = load_or_fetch_kddcup99(dataset_root)
    frame = sample_dataset(frame, max_samples=max_samples, seed=seed)
    train_frame, val_frame, test_frame = _split_frame(frame, seed)

    scaler = StandardScaler()
    train_features = scaler.fit_transform(train_frame[KDD_FEATURES])
    val_features = scaler.transform(val_frame[KDD_FEATURES])
    test_features = scaler.transform(test_frame[KDD_FEATURES])

    train_labels = _to_binary(train_frame["label"])
    val_labels = _to_binary(val_frame["label"])
    test_labels = _to_binary(test_frame["label"])

    x_train, y_train = _make_sequences(train_features, train_labels, seq_len)
    x_val, y_val = _make_sequences(val_features, val_labels, seq_len)
    x_test, y_test = _make_sequences(test_features, test_labels, seq_len)

    bundle = TrainingBundle(
        train_loader=build_loader(x_train, y_train, batch_size=batch_size, shuffle=True),
        val_loader=build_loader(x_val, y_val, batch_size=batch_size, shuffle=False),
        test_loader=build_loader(x_test, y_test, batch_size=batch_size, shuffle=False),
    )

    device = torch.device("cpu")
    lstm = train_binary_model(
        LSTMClassifier(input_dim=len(KDD_FEATURES)),
        bundle=bundle,
        epochs=epochs,
        learning_rate=1e-3,
        device=device,
    )
    mlp = train_binary_model(
        MLPBaseline(input_dim=seq_len * len(KDD_FEATURES)),
        bundle=bundle,
        epochs=epochs,
        learning_rate=1e-3,
        device=device,
    )

    lstm_metrics = evaluate_binary_model(lstm, bundle.test_loader)
    mlp_metrics = evaluate_binary_model(mlp, bundle.test_loader)

    torch.save(lstm.state_dict(), output_root / "lstm.pt")
    torch.save(mlp.state_dict(), output_root / "mlp.pt")
    metrics = {
        "dataset": {
            "feature_count": len(KDD_FEATURES),
            "max_samples": max_samples,
            "rows_used": len(frame),
            "sequence_length": seq_len,
            "train_sequences": int(len(x_train)),
            "validation_sequences": int(len(x_val)),
            "test_sequences": int(len(x_test)),
        },
        "lstm": lstm_metrics,
        "mlp": mlp_metrics,
    }
    write_json(output_root / "metrics.json", metrics)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the paper-inspired KDD Cup 1999 anomaly detector.")
    parser.add_argument("--dataset-root", type=Path, default=Path("data/raw/kddcup99"))
    parser.add_argument("--output-root", type=Path, default=Path("models/kdd"))
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-samples", type=int, default=10000)
    parser.add_argument("--seq-len", type=int, default=10)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=128)
    args = parser.parse_args()
    ensure_output_directories()
    metrics = run_training_pipeline(
        dataset_root=args.dataset_root,
        output_root=args.output_root,
        seed=args.seed,
        max_samples=args.max_samples,
        seq_len=args.seq_len,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )
    print(metrics)


if __name__ == "__main__":
    main()

