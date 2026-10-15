"""Visible, consent-based input audit application.

The demo records text only when the user clicks Record. It deliberately does
not monitor keystrokes or mouse activity in other applications.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from config import EMAIL_ENABLED, ENCRYPT_LOGS
from utils.encryptor import encrypt_file
from utils.logger import AuditLogger
from utils.mailer import send_report


class PyKeyLoggerDemo:
    """A small GUI demonstrating explicit input auditing and file protection."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.audit = AuditLogger()
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="audit-worker")
        self._closed = False
        self.root.title("PyKeyLogger — Consent-Based Audit Demo")
        self.root.geometry("640x380")
        self.root.minsize(540, 340)

        tk.Label(root, text="Educational Input Audit", font=("Arial", 17, "bold")).pack(pady=(20, 8))
        tk.Label(
            root,
            text=(
                "This visible demo records only text you submit here. "
                "It does not capture input from other apps. Avoid entering secrets."
            ),
            wraplength=570,
            justify="center",
        ).pack(pady=4)

        self.input = tk.Entry(root, width=68)
        self.input.pack(padx=20, pady=18, ipady=5)
        self.input.bind("<Return>", self._submit_from_enter)
        tk.Button(root, text="Record submitted text", command=self.save).pack(pady=4)
        self.status = tk.Label(root, text="Ready — no input has been recorded yet.", wraplength=580)
        self.status.pack(pady=16)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _submit_from_enter(self, _event: tk.Event) -> str:
        """Treat Enter as an explicit submit inside this application's field."""
        self.save()
        return "break"

    def save(self) -> None:
        """Write one explicitly submitted sample and process closed logs."""
        value = self.input.get()
        if not value.strip():
            messagebox.showinfo("No input", "Enter non-empty demo text first.")
            return
        try:
            self.audit.write("demo_button_click", "Record submitted text")
            current_path, rotated_path = self.audit.write("submitted_text", value)
        except OSError as exc:
            messagebox.showerror("Write failed", str(exc))
            return
        self.input.delete(0, tk.END)
        self.status.config(text=f"Recorded one submitted event in {current_path.name}")
        # A rotated file is no longer being appended to, so it is safe to process.
        if rotated_path:
            self._process_closed_log(rotated_path)

    def _process_closed_log(self, path: Path) -> None:
        """Schedule encryption and, if enabled, report delivery in a worker."""
        if ENCRYPT_LOGS:
            future = self.pool.submit(encrypt_file, path)
            if EMAIL_ENABLED:
                future.add_done_callback(self._email_encrypted_result)
        elif EMAIL_ENABLED:
            self.pool.submit(send_report, path)

    @staticmethod
    def _email_encrypted_result(future) -> None:
        """Email only a successfully encrypted report; failures remain visible."""
        try:
            encrypted_path = future.result()
            send_report(encrypted_path)
        except Exception as exc:  # Report background errors instead of silently hiding them.
            print(f"Background report processing failed: {exc}")

    def close(self) -> None:
        """Rotate and process the current log before shutting down."""
        if self._closed:
            return
        self._closed = True
        try:
            path = self.audit.current_path
            if path.exists() and path.stat().st_size:
                # Current log is no longer used after the window closes.
                self._process_closed_log(path)
        except OSError as exc:
            print(f"Could not finalize audit log: {exc}")
        self.pool.shutdown(wait=True, cancel_futures=False)
        self.root.destroy()


def main() -> None:
    """Start the visible demo UI."""
    root = tk.Tk()
    PyKeyLoggerDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
