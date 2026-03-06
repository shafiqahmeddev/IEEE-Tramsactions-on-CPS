# Optimizing V2G Dynamics

Official implementation repository for the article *Optimizing V2G Dynamics: An AI-Enhanced Secure Protocol for Energy Management in Industrial Cyber-Physical Systems*.

## Overview

This codebase implements the article's secure Vehicle-to-Grid workflow for industrial cyber-physical systems, combining:
- a multi-entity authentication protocol with user, gateway, charge-station, and control-server roles
- software-emulated WPUF and RPUF components
- protocol cost-analysis utilities
- an anomaly-detection pipeline on KDD Cup 1999 using an LSTM model with an MLP baseline

## Highlights

- End-to-end protocol flow with session-key establishment and message tracing
- Secure-by-default cryptographic implementation choices for hashing, key derivation, and replay protection
- Table-generation utilities for implementation-side performance summaries
- Modular Python package layout for protocol, ML, and analysis components
- Automated test coverage for protocol behavior, PUF logic, cost utilities, and ML execution paths

## Repository Layout

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

## Getting Started

```powershell
cd "CPS Implementation"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
.\.venv\Scripts\python.exe -m pytest -q
```

## Primary Commands

Protocol demonstration:

```powershell
.\.venv\Scripts\python.exe -m v2g_cps.protocol.demo
```

Model training:

```powershell
.\.venv\Scripts\python.exe -m v2g_cps.ml.train --dataset-root data/raw/kddcup99
```

Full implementation pipeline:

```powershell
.\.venv\Scripts\python.exe -m v2g_cps.run_pipeline
```

## Local Outputs

Running the implementation pipeline locally produces:
- protocol traces
- implementation tables and summaries
- a Markdown implementation report
- ML metrics and local model checkpoints

These outputs are generated locally and intentionally ignored by Git.

## Security

The implementation uses secure-by-default engineering choices, including:
- transcript-bound HMAC-SHA256
- HKDF-based session-key derivation
- ephemeral P-256 ECDH
- scrypt password verifiers
- constant-time comparisons for sensitive equality checks
- replay-cache enforcement and timestamp freshness checks

See `SECURITY.md` for disclosure guidance and repository publishing rules.

## License

This repository is licensed under the MIT License. Third-party papers, datasets, and referenced publications remain subject to their own licenses and redistribution restrictions.
