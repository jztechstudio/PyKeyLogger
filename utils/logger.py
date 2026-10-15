"""Thread-safe audit writer with time- and size-based log rotation."""

from datetime import datetime, timezone
from pathlib import Path
import threading

from config import LOG_DIR, LOG_INTERVAL, MAX_LOG_BYTES


class AuditLogger:
    """Write explicit application-submitted events to local text logs."""

    def __init__(self, directory: Path = LOG_DIR) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._started_at = datetime.now(timezone.utc)
        self._path = self._new_path()

    def _new_path(self) -> Path:
        """Generate a unique UTC-based filename."""
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        return self.directory / f"audit_{stamp}.txt"

    def _rotate_if_needed(self, incoming_bytes: int = 0) -> Path | None:
        """Rotate before writing if interval or size threshold is reached."""
        elapsed = (datetime.now(timezone.utc) - self._started_at).total_seconds()
        size = self._path.stat().st_size if self._path.exists() else 0
        if elapsed >= LOG_INTERVAL or (size and size + incoming_bytes > MAX_LOG_BYTES):
            old_path = self._path if self._path.exists() and size else None
            self._path = self._new_path()
            self._started_at = datetime.now(timezone.utc)
            return old_path
        return None

    def write(self, event: str, value: str) -> tuple[Path, Path | None]:
        """Append an audit event and return (written_path, rotated_path)."""
        timestamp = datetime.now(timezone.utc).isoformat()
        safe_event = str(event).replace("\t", " ").replace("\n", " ")
        safe_value = str(value).replace("\r", "\\r").replace("\n", "\\n")
        line = f"{timestamp}\t{safe_event}\t{safe_value}\n"
        with self._lock:
            rotated_path = self._rotate_if_needed(len(line.encode("utf-8")))
            with self._path.open("a", encoding="utf-8") as stream:
                stream.write(line)
                stream.flush()
            return self._path, rotated_path

    @property
    def current_path(self) -> Path:
        """Return the log path currently receiving submitted events."""
        return self._path
