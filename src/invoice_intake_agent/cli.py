"""Command line interface for the invoice intake agent."""

import argparse
import asyncio

from .utils.runtime import set_runtime

from .app import run_app


def main() -> None:
    """Main entry point for the invoice intake agent."""

    p = argparse.ArgumentParser()
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--log-level", choices=["minimal", "verbose", "debug"], default=None)
    p.add_argument("--no-color", action="store_true")
    args = p.parse_args()

    set_runtime(log_level=args.log_level, verbose=args.verbose, color=not args.no_color)
    asyncio.run(run_app())
