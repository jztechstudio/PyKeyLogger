"""Central settings for the PyKeyLogger educational audit demo."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"

# A new plaintext file is started after this many seconds.
LOG_INTERVAL = 60
ENCRYPT_LOGS = True
EMAIL_ENABLED = False

SMTP_HOST = os.getenv("PYKEYLOGGER_SMTP_HOST", "")
SMTP_PORT = int(os.getenv("PYKEYLOGGER_SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("PYKEYLOGGER_SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("PYKEYLOGGER_SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("PYKEYLOGGER_EMAIL_FROM", "")
EMAIL_TO = os.getenv("PYKEYLOGGER_EMAIL_TO", "")

# Keep logs small for easier review. Rotation also happens on the timer.
MAX_LOG_BYTES = 1_000_000
