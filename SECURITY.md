# Security Policy

## Supported Scope

This repository is an implementation project. Security-sensitive areas include:
- cryptographic protocol code under `CPS Implementation/src/v2g_cps/protocol/`
- dataset handling under `CPS Implementation/src/v2g_cps/ml/`
- generated outputs that may contain runtime trace material

## Reporting a Vulnerability

If you find a security issue, report it privately to:
- `sa23281@essex.ac.uk`

Please include:
- a concise description of the issue
- affected files or modules
- relevant steps to trigger the issue
- expected impact

Do not open a public issue for unpatched vulnerabilities.

## Publishing Rules

- Do not commit secrets, API tokens, private keys, or credential files.
- Do not commit local virtual environments, caches, model checkpoints, or raw downloaded datasets unless there is a specific review reason.
- Do not publish third-party licensed papers or datasets unless redistribution rights are clear.
- Treat protocol traces and derived session material as local artifacts; regenerate them locally when needed.
