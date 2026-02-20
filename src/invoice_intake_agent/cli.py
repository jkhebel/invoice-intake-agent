"""Command line interface for the invoice intake agent."""

import argparse
import asyncio

from .app import run_app
from .utils.runtime import set_runtime


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""

    description = (
        "Invoice Intake Agent (OpenAI Agents SDK\n\n)"
        "Processes a local inbound email JSON + its PDF attachment "
        "to extract invoice data and notifies Customer Service."
    )

    epilog = (
        "Examples:\n"
        "  uv run invoice-intake-agent\n"
        "  uv run invoice-intake-agent --verbose\n"
        "  uv run invoice-intake-agent --log-level debug\n"
        "  uv run invoice-intake-agent --no-color\n"
    )

    p = argparse.ArgumentParser(
        prog="invoice-intake-agent",
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose console output (stream model output, including tool calls and nested agents).",
    )
    p.add_argument(
        "--log-level",
        choices=["minimal", "verbose", "debug"],
        default=None,
        help="Set logging verbosity explicitly. Overrides --verbose.",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colorized/stylized console output.",
    )

    # TODO(cli): Add `--email PATH` to point at a specific inbound email JSON (default: first in ./data).
    # TODO(cli): Add `--data-dir PATH` to set the input folder (default: ./data).
    # TODO(cli): Add `--outputs-dir PATH` to set the outputs folder (default: ./outputs).
    # TODO(cli): Add `--artifacts-dir PATH` to set artifacts folder (default: ./outputs/artifacts/<run_id>/).
    # TODO(cli): Add `--clean` to delete artifacts/outputs from prior runs (confirm unless --yes).
    # TODO(cli): Add `--clean-artifacts` and `--clean-outputs` to clean selectively.
    # TODO(cli): Add `--yes` to skip confirmation prompts for destructive actions (clean).
    # TODO(cli): Add `--dry-run` to run extraction without writing notification files.
    # TODO(cli): Add `--format {json,text,both}` to control notification output format.
    # TODO(cli): Add `--max-turns N` to control orchestrator max turns (useful for debugging costs).
    # TODO(cli): Add `--model {gpt-5-mini,gpt-5-nano}` to override the default model selection.
    # TODO(cli): Add `--profile` to print timing metrics per stage/tool.
    # TODO(cli): Add `--quiet` to suppress all non-error console output.

    return p


def main() -> None:
    """Main entry point for the invoice intake agent."""

    parser = build_parser()
    args = parser.parse_args()

    set_runtime(log_level=args.log_level, verbose=args.verbose, color=not args.no_color)

    asyncio.run(run_app())


if __name__ == "__main__":
    main()
