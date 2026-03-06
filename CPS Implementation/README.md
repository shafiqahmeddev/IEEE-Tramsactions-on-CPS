# CPS Implementation Workspace

This directory contains the installable Python package, the automated test suite, and the local execution pipeline for the article implementation.

## Structure

- `src/v2g_cps/`: protocol, ML, and analysis modules
- `tests/`: automated verification suite
- `data/`, `models/`, `reports/`, `results/`: local runtime outputs

## Commands

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m v2g_cps.protocol.demo
.\.venv\Scripts\python.exe -m v2g_cps.ml.train --dataset-root data/raw/kddcup99
.\.venv\Scripts\python.exe -m v2g_cps.run_pipeline
```
