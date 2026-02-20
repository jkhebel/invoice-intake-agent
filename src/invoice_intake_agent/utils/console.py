"""Console utilities for the invoice intake agent."""

import sys

from contextlib import contextmanager
from typing import Iterator, Optional

from rich.console import Console
from rich.text import Text
from rich.theme import Theme

from .runtime import RUNTIME


# --- Setup Console -----------------------------------------------------------

THEME = Theme(
    {
        "main": "bold",
        "orch": "bold blue",
        "invoice": "bold green",
        "tool": "bold magenta",
        "sys": "yellow",
        "dim": "dim",
        "err": "bold red",
        "ok": "bold green",
        "rule": "grey50",
    }
)

# Use stderr for console output for nested streaming
console = Console(theme=THEME, file=sys.stderr, force_terminal=True)

# --- Helper functions --------------------------------------------------------


def _flush() -> None:
    """Force-flush the underlying console output stream (useful for token streaming)."""
    try:
        console.file.flush()
    except Exception:
        pass


def _prefix(role: str, style: str) -> Text:
    role_up = role.upper()
    t = Text()
    t.append(f"[{role_up}]", style=style)
    t.append(" ")
    return t


def emit(role: str, message: str, *, style: str, end: str = "\n") -> None:
    """
    Print a single line with a consistent prefix.
    """
    if not RUNTIME.color:
        # De-colorize: render plain prefix then message
        console.print(f"[{role}] {message}", end=end, highlight=False, soft_wrap=True)
        _flush()
        return

    prefix = _prefix(role, style)
    console.print(prefix, message, end=end, highlight=False, soft_wrap=True)
    _flush()


# --- Logging/Printing functions ----------------------------------------------


def pre(role: str, *, style: str | None = None) -> None:
    """Print the prefix for a role (no trailing newline)."""
    role_up = role.upper()

    if not RUNTIME.color:
        console.print(f"[{role_up}]", end=" ")
        _flush()
        return

    if style is None:
        # Default: use a known theme style if present; otherwise fall back to "main".
        candidate = role_up.lower()
        style = candidate if candidate in THEME.styles else "main"

    prefix = _prefix(role_up, style=style)
    console.print(prefix, end="")
    _flush()


def print(message: str, *, style: str | None = None, end: str = "") -> None:
    """
    Print output to the console.
    """
    if not RUNTIME.color:
        # De-colorize: render plain prefix then message
        console.print(f"{message}", end=end, highlight=False, soft_wrap=True)
        _flush()
        return

    if style is not None:
        message = f"[{style}]{message}[/{style}]"

    console.print(message, end=end, highlight=False, soft_wrap=True)
    _flush()


def orch(message: str, *, end: str = "\n") -> None:
    emit("ORCHESTRATOR", message, style="orch", end=end)


def invoice(message: str, *, end: str = "\n") -> None:
    emit("INVOICE_AGENT", message, style="invoice", end=end)


def tool(message: str, *, end: str = "\n") -> None:
    emit("TOOL", message, style="tool", end=end)


def sysmsg(message: str, *, end: str = "\n") -> None:
    emit("SYSTEM", message, style="sys", end=end)


def dim(role: str, message: str, *, end: str = "\n") -> None:
    """
    Dim 'thinking-like' line (stage updates).
    """
    emit(role, message, style="dim", end=end)


def error(message: str, *, end: str = "\n") -> None:
    emit("ERROR", message, style="err", end=end)


def ok(message: str, *, end: str = "\n") -> None:
    emit("OK", message, style="ok", end=end)


def rule(title: str, *, style: str | None = None) -> None:
    """
    Separator line.
    """
    if RUNTIME.color:
        if not style:
            console.rule(title, style="rule")
        else:
            console.rule(f"[{style}]" + title + f"[/{style}]", style="rule")
        _flush()
    else:
        console.print(f"--- {title} ---")
        console.print("\n")
        _flush()


@contextmanager
def status(message: str, *, spinner: str = "dots") -> Iterator[None]:
    """Spinner for quiet/background operations.
    Avoid using while streaming tokens.
    """

    # if not RUNTIME.verbose:
    #     # Minimal mode, no spinner
    #     yield
    #     return

    with console.status(message, spinner=spinner):
        yield
