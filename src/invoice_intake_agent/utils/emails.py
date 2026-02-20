"""Tools for working with emails."""

import json
from pathlib import Path
from typing import Dict, Any, List


class EmailLoadError(RuntimeError):
    """Error loading the email."""


def load_emails(path: str | Path = "inputs") -> List[Dict[str, Any]]:
    """Load all emails from a directory."""
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise EmailLoadError(f"Email directory not found: {path}")
    emails = []
    for file in path.glob("*.json"):
        emails.append(Email(file))
    return emails


class Email:
    def __init__(self: Dict[str, Any], path: str | Path = "inputs/Email.json"):
        self.source_path = Path(path).expanduser().resolve()
        self.email = self._load_email(self.source_path)

    def __getitem__(self, key: str) -> Any:
        return self.email[key]

    def to_dict(self) -> dict[str, Any]:
        return self.email

    def _load_email(self, path: Path) -> dict[str, Any]:
        """Load an email from a file."""
        if not path.exists():
            raise EmailLoadError(f"Email file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            email = json.load(f)

        return email["Message"]

    def get_pdf_path(self) -> Path:
        """Get the PDF attachment path from the email."""
        for attachment in self.email["Attachments"]:
            if attachment["ContentType"] == "application/pdf":
                return Path(self.source_path.parent / attachment["Name"])
        raise EmailLoadError("No PDF attachment found in email")


def load_email(path: str | Path = "inputs/Email.json") -> Email:
    """Load an email from a JSON file."""
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise EmailLoadError(f"Email file not found: {path}")
    if path.suffix.lower() != ".json":
        raise EmailLoadError(f"Email file must be a JSON file: {path}")
    return Email(path)
