"""Command line interface for the invoice intake agent."""

import argparse
import asyncio
from .app import run_app


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose", "-v", default=False, type=bool, help="Verbose output"
    )
    # parser.add_argument("--input", required=False)
    args = parser.parse_args()

    # run(args.input)
    asyncio.run(run_app(verbose=args.verbose))
    return 0
