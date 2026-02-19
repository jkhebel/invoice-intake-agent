"""Application for the invoice intake agent."""

import asyncio

# from .core.pipeline import process_invoice
from .agents.orchestrator import run_agent


def run() -> None:
    asyncio.run(run_agent())
