"""Fernet file encryption and command-line decryption helpers.

Fernet uses AES-128-CBC with HMAC-SHA256 authentication; it is not AES-256.
"""

import argparse
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from config import BASE_DIR

KEY_PATH = BASE_DIR / "secret.key"


def load_or_create_key() -> bytes:
    """Read the local key or create it exclusively with restrictive mode."""
    if KEY_PATH.exists():
        key = KEY_PATH.read_bytes()
        # Validates key format before any data processing.
        Fernet(key)
        return key
    key = Fernet.generate_key()
    try:
        fd = os.open(KEY_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return KEY_PATH.read_bytes()
    with os.fdopen(fd, "wb") as stream:
        stream.write(key)
    return key


def encrypt_file(path: Path) -> Path:
    """Encrypt a log to a new .enc file, then remove the plaintext file."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    destination = path.with_suffix(path.suffix + ".enc")
    encrypted = Fernet(load_or_create_key()).encrypt(path.read_bytes())
    # 'xb' prevents accidental overwrite of existing encrypted data.
    with destination.open("xb") as stream:
        stream.write(encrypted)
    path.unlink()
    return destination


def decrypt_file(path: Path) -> Path:
    """Decrypt an encrypted file into a new sibling file without overwriting."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    destination = path.with_suffix(".decrypted.txt")
    try:
        plaintext = Fernet(load_or_create_key()).decrypt(path.read_bytes())
    except InvalidToken as exc:
        raise ValueError("Decryption failed: invalid ciphertext or key.") from exc
    with destination.open("xb") as stream:
        stream.write(plaintext)
    return destination


def main() -> None:
    """Parse CLI arguments for explicit log decryption."""
    parser = argparse.ArgumentParser(description="PyKeyLogger log encryption utility")
    parser.add_argument("--decrypt", type=Path, metavar="FILE", help="decrypt a .enc file")
    args = parser.parse_args()
    if not args.decrypt:
        parser.print_help()
        return
    try:
        output = decrypt_file(args.decrypt)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Decrypted file: {output}")


if __name__ == "__main__":
    main()
