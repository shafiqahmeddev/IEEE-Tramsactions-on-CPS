# AI-Enhanced Secure V2G Protocol Implementation

Python implementation of the article's secure Vehicle-to-Grid authentication and anomaly-detection workflow for industrial cyber-physical systems.

## Overview

This repository contains:
- a multi-entity protocol implementation with user, gateway, charge-station, and control-server roles
- software-emulated WPUF and RPUF components
- cost-analysis utilities for the protocol tables used in the article
- an anomaly-detection pipeline on KDD Cup 1999 using an LSTM model and an MLP baseline

## Repository Structure

```text
.
|-- CPS Implementation/
|   |-- pyproject.toml
|   |-- README.md
|   |-- src/v2g_cps/
|   |   |-- protocol/
|   |   |-- ml/
|   |   `-- analysis/
|   `-- tests/
|-- README.md
|-- SECURITY.md
`-- LICENSE
```

## Quick Start

```powershell
cd "CPS Implementation"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
.\.venv\Scripts\python.exe -m pytest -q
```

## Main Commands

Protocol demo:

```powershell
.\.venv\Scripts\python.exe -m v2g_cps.protocol.demo
```

ML training pipeline:

```powershell
.\.venv\Scripts\python.exe -m v2g_cps.ml.train --dataset-root data/raw/kddcup99
```

Full implementation pipeline:

```powershell
.\.venv\Scripts\python.exe -m v2g_cps.run_pipeline
```

## Generated Outputs

Running the full pipeline locally produces:
- protocol traces
- implementation tables and summaries
- a Markdown implementation report
- ML metrics and local model checkpoints

These outputs are generated locally and ignored by Git on purpose.

## Security and Cryptography

The implementation uses secure-by-default engineering choices, including:
- transcript-bound HMAC-SHA256
- HKDF-based session-key derivation
- ephemeral P-256 ECDH
- scrypt password verifiers
- constant-time comparisons for sensitive equality checks
- replay-cache enforcement and timestamp freshness checks

## Public Repo Hygiene

- Do not commit secrets, API tokens, private keys, or local `.env` files.
- Do not commit virtual environments, caches, raw datasets, generated traces, or model checkpoints.
- Do not commit third-party licensed PDFs or datasets unless redistribution rights are clear.

See `SECURITY.md` for disclosure guidance.

## License

This repository is licensed under the MIT License. Third-party papers, datasets, and referenced publications remain subject to their own licenses and redistribution restrictions.
