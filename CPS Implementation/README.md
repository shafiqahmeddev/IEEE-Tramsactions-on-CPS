# V2G CPS Implementation Package

This directory contains the Python package, test suite, and local-output pipeline for the article implementation.

## Main Commands

```powershell
.\.venv\Scripts\python.exe -m v2g_cps.protocol.demo
.\.venv\Scripts\python.exe -m v2g_cps.ml.train --dataset-root data/raw/kddcup99
.\.venv\Scripts\python.exe -m v2g_cps.run_pipeline
```

## Contents

- `src/v2g_cps/`: protocol, ML, and analysis modules
- `tests/`: automated verification suite
- `data/`, `models/`, `reports/`, `results/`: local runtime outputs
