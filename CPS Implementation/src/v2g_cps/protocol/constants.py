from __future__ import annotations

PAPER_SECURITY_FEATURES = [
    ("F1", "EV impersonation"),
    ("F2", "CS impersonation"),
    ("F3", "Man in the middle"),
    ("F4", "Distributed denial of service"),
    ("F5", "Privileged insider"),
    ("F6", "Replay"),
    ("F7", "User anonymity"),
    ("F8", "Forward and backward secrecy"),
    ("F9", "Desynchronization"),
    ("F10", "Physical attacks"),
    ("F11", "Machine learning attacks"),
]

PAPER_TABLE_III_ROWS = [
    {"protocol": "[4]", "F1": "N", "F2": "N", "F3": "N", "F4": "Y", "F5": "Y", "F6": "N", "F7": "Y", "F8": "Y", "F9": "N", "F10": "N", "F11": "N"},
    {"protocol": "[5]", "F1": "Y", "F2": "Y", "F3": "N", "F4": "N", "F5": "Y", "F6": "Y", "F7": "Y", "F8": "Y", "F9": "N", "F10": "N", "F11": "N"},
    {"protocol": "[7]", "F1": "Y", "F2": "Y", "F3": "Y", "F4": "Y", "F5": "Y", "F6": "N", "F7": "N", "F8": "Y", "F9": "N", "F10": "N", "F11": "N"},
    {"protocol": "[8]", "F1": "Y", "F2": "Y", "F3": "Y", "F4": "N", "F5": "N", "F6": "Y", "F7": "Y", "F8": "Y", "F9": "N", "F10": "Y", "F11": "N"},
    {"protocol": "[9]", "F1": "Y", "F2": "N", "F3": "N", "F4": "Y", "F5": "Y", "F6": "Y", "F7": "Y", "F8": "N", "F9": "Y", "F10": "N", "F11": "N"},
    {"protocol": "[10]", "F1": "Y", "F2": "Y", "F3": "Y", "F4": "Y", "F5": "Y", "F6": "Y", "F7": "Y", "F8": "Y", "F9": "N", "F10": "Y", "F11": "Y"},
    {"protocol": "[11]", "F1": "Y", "F2": "Y", "F3": "N", "F4": "Y", "F5": "N", "F6": "Y", "F7": "Y", "F8": "N", "F9": "Y", "F10": "Y", "F11": "Y"},
]

PAPER_TABLE_IV_ROWS = [
    {
        "reference": "[4]",
        "formula": "4Tpm + Tm + 5Th",
        "operation_counts": {"Tpm": 4, "Tm": 1, "Th": 5},
        "reported_ms": 2802.0,
        "reported_communication_bytes": 280,
    },
    {
        "reference": "[5]",
        "formula": "3Tpm + Tm + 6Th",
        "operation_counts": {"Tpm": 3, "Tm": 1, "Th": 6},
        "reported_ms": 2274.0,
        "reported_communication_bytes": 304,
    },
    {
        "reference": "[7]",
        "formula": "Tfe + 9Th",
        "operation_counts": {"Tfe": 1, "Th": 9},
        "reported_ms": 218.0,
        "reported_communication_bytes": 516,
    },
    {
        "reference": "[8]",
        "formula": "Tfe + 2TPUF + 7Th",
        "operation_counts": {"Tfe": 1, "TPUF": 2, "Th": 7},
        "reported_ms": 110.9,
        "reported_communication_bytes": 220,
    },
    {
        "reference": "[9]",
        "formula": "Tfe + TPUF + 3Th",
        "operation_counts": {"Tfe": 1, "TPUF": 1, "Th": 3},
        "reported_ms": 185.4,
        "reported_communication_bytes": 312,
    },
    {
        "reference": "[10]",
        "formula": "TWPUF + 2TRPUF + 7Th",
        "operation_counts": {"TWPUF": 1, "TRPUF": 2, "Th": 7},
        "reported_ms": 63.6,
        "reported_communication_bytes": 208,
    },
    {
        "reference": "[11]",
        "formula": "TWPUF + 2TRPUF + 7Th",
        "operation_counts": {"TWPUF": 1, "TRPUF": 2, "Th": 7},
        "reported_ms": 63.6,
        "reported_communication_bytes": 208,
    },
    {
        "reference": "Proposed",
        "formula": "TWPUF + 2TRPUF + 8Th",
        "operation_counts": {"TWPUF": 1, "TRPUF": 2, "Th": 8},
        "reported_ms": 65.2,
        "reported_communication_bytes": 216,
    },
]

PAPER_TABLE_V_USER_DEVICE = {
    "Tpm": 5.09,
    "Tm": 20.23,
    "Th": 0.0186,
    "TSenc": 0.053,
    "TPUF": 3.81,
    "TWPUF": 2.221,
    "TRPUF": 3.321,
}

PAPER_TABLE_V_ESP_CS = {
    "Tpm": 2.4,
    "Tm": 12.4,
    "Th": 0.013,
    "TSenc": 0.039,
    "TPUF": 2.57,
    "TWPUF": 1.79,
    "TRPUF": 2.34,
}

PAPER_OPERATION_ORDER = ["Tpm", "Tm", "Th", "TSenc", "TPUF", "TWPUF", "TRPUF"]

PAPER_MESSAGE_BIT_BREAKDOWN = {
    "MSG1": 256,
    "MSG2": 512,
    "MSG3": 320,
    "MSG4": 576,
}

PAPER_MESSAGE_FIELDS = {
    "MSG1": ["EVpid", "rv", "EL", "L1"],
    "MSG2": ["CSid", "rcs", "LScs", "L2"],
    "MSG3": ["Paper-reported payload"],
    "MSG4": ["Paper-reported payload"],
}

PAPER_TOTAL_COMMUNICATION_BITS = 1728
PAPER_TOTAL_COMMUNICATION_BYTES = 216

SECURITY_FLAG_DESCRIPTIONS = {
    "F1": "Password-gated login plus server-issued user token prevent EV impersonation.",
    "F2": "Gateway-verified station attestation and PUF proof prevent CS impersonation.",
    "F3": "Transcript-bound authentication tags and ephemeral ECDH resist man-in-the-middle attacks.",
    "F4": "Freshness windows and early reject logic reduce unauthenticated request amplification.",
    "F5": "Only salted password verifiers and derived tokens are stored; raw passwords are never stored.",
    "F6": "Timestamps plus nonce replay caches detect duplicate authentication attempts.",
    "F7": "Messages carry a pseudonym instead of the raw user identity.",
    "F8": "Per-session ECDH keys provide forward and backward secrecy.",
    "F9": "The protocol avoids synchronized counters, reducing desynchronization failure modes.",
    "F10": "WPUF/RPUF attestations model tamper-sensitive physical protection.",
    "F11": "The reconfigurable PUF epoch changes after each successful session to frustrate model building.",
}

DEFAULT_PSEUDONYM_BYTES = 16
DEFAULT_NONCE_BYTES = 16
DEFAULT_TAG_BYTES = 32
DEFAULT_RESPONSE_BYTES = 16
DEFAULT_TIMESTAMP_TOLERANCE_SECONDS = 300

