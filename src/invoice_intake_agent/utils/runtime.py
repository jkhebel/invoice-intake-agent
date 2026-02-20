"""Runtime utilities for the invoice intake agent."""

from dataclasses import dataclass
from enum import IntEnum


class LogLevel(IntEnum):
    """Logging levels."""

    MINIMAL = 0
    VERBOSE = 1
    DEBUG = 2


@dataclass
class RuntimeConfig:
    """Runtime configuration."""

    log_level: LogLevel = LogLevel.MINIMAL
    color: bool = True

    @property
    def verbose(self) -> bool:
        """Whether to log verbose messages."""
        return self.log_level >= LogLevel.VERBOSE

    @property
    def debug(self) -> bool:
        """Whether to log debug messages."""
        return self.log_level >= LogLevel.DEBUG


# Global runtime config
RUNTIME = RuntimeConfig()


def set_runtime(
    *, log_level: str | None = None, verbose: bool = False, color: bool = True
) -> None:
    """Set the runtime configuration from CLI arguments."""
    level = RUNTIME.log_level

    if log_level:
        log_level_str = log_level.strip().lower()
        if log_level_str in ("minimal", "min", "0"):
            level = LogLevel.MINIMAL
        elif log_level_str in ("verbose", "v", "1"):
            level = LogLevel.VERBOSE
        elif log_level_str in ("debug", "d", "2"):
            level = LogLevel.DEBUG
        else:
            raise ValueError(f"Invalid log level: {log_level!r}")

    # Verbose supersedes minimal
    if verbose and level == LogLevel.MINIMAL:
        level = LogLevel.VERBOSE

    RUNTIME.log_level = level
    RUNTIME.color = color
