# PyKeyLogger — Secure Input Audit Demo

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Encryption](https://img.shields.io/badge/Encryption-Fernet%20%2F%20AES--256-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

A recruiter-friendly Python security project demonstrating application-scoped input auditing, authenticated encryption, timed log rotation, optional SMTP delivery, and modular code organization.

> **Privacy by design:** This demo records only text explicitly submitted inside its own visible input window. It does not install global keyboard hooks, capture passwords from other applications, monitor other windows, or run covertly in the background.

## Features

- Explicitly submitted text audit events
- Application button / mouse-click event logging
- Authenticated file encryption using `cryptography`'s Fernet construction (AES-128-CBC + HMAC-SHA256; do not mislabel this as AES-256)
- Configurable time-based log rotation (default: 60 seconds)
- Optional SMTP delivery of encrypted reports
- Background encryption and mail processing
- CLI decryption: `python -m utils.encryptor --decrypt logs/file.txt.enc`
- Separation of configuration, logging, encryption, and mail delivery
- Python 3.10+; UI uses the Python standard-library `tkinter`

## Project layout

```text
PyKeyLogger/
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── keylogger.py
├── config.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── encryptor.py
│   └── mailer.py
└── logs/
    └── .gitkeep
```

## Install

Python 3.10 or newer is required.

```bash
python -m venv venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux / macOS**
```bash
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the demo

From the project directory:

```bash
python keylogger.py
```

Type sample text into the visible demo field and click **Record submitted text**. Only the submitted value is saved. Closing the window stops the worker pool.

## Decrypt a log

Encrypted log files use the `.enc` suffix. From the project directory:

```bash
python -m utils.encryptor --decrypt logs/audit_20261015T120000Z.txt.enc
```

A decrypted copy is written alongside the encrypted file with a `.decrypted.txt` suffix. Existing output files are not overwritten.

## Configuration

Adjust `config.py` for log rotation, encryption, email enablement, and the output directory. SMTP settings can be supplied with environment variables:

- `PYKEYLOGGER_SMTP_HOST`
- `PYKEYLOGGER_SMTP_PORT` (default `587`)
- `PYKEYLOGGER_SMTP_USERNAME`
- `PYKEYLOGGER_SMTP_PASSWORD`
- `PYKEYLOGGER_EMAIL_FROM`
- `PYKEYLOGGER_EMAIL_TO`

Email delivery is disabled by default. To enable it, set `EMAIL_ENABLED = True` in `config.py`. Use a dedicated SMTP credential or app password; do not commit credentials.

## Encryption and key management

The app creates `secret.key` on first use. Keep this key private and backed up securely; losing it means encrypted logs cannot be decrypted. Restrict access to both the key and log files. Fernet uses AES-128-CBC with HMAC-SHA256 authentication, so this project intentionally does not claim AES-256.

## Screenshots

Add screenshots here, for example:

- `screenshots/demo-window.png` — visible input-audit demo
- `screenshots/encrypted-log.png` — encrypted output in the logs directory

## Ideas for future improvements

- Unit tests for rotation and encryption
- Structured JSON audit events
- A key-management integration
- Explicit retention policies and configurable redaction
- CI checks with `ruff` and `pytest`

## Disclaimer

This tool is for educational purposes only. Do not dictionary use on anyone without consent.