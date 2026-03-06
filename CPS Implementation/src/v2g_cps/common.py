from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
RESULTS_ROOT = PROJECT_ROOT / "results"
REPORTS_ROOT = PROJECT_ROOT / "reports"
MODELS_ROOT = PROJECT_ROOT / "models"
TRACES_ROOT = RESULTS_ROOT / "traces"


def ensure_output_directories() -> dict[str, Path]:
    directories = {
        "data": DATA_ROOT,
        "results": RESULTS_ROOT,
        "reports": REPORTS_ROOT,
        "models": MODELS_ROOT,
        "traces": TRACES_ROOT,
    }
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)
    return directories


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except ImportError:
        pass


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

