"""Application for the invoice intake agent."""

import sys
import asyncio
import argparse

from agents import Runner, InputGuardrailTripwireTriggered
from openai.types.responses import ResponseTextDeltaEvent

# from .core.pipeline import process_invoice
from .agents.orchestrator import build_orchestrator_agent


async def run_app(verbose: bool = False) -> None:
    """Run the invoice intake orchestration agent with streaming output."""

    orchestrator_agent = build_orchestrator_agent()
    user_input = "Process the inbound email and its PDF attachment."

    try:
        result = Runner.run_streamed(orchestrator_agent, user_input, max_turns=6)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                print(event.data.delta, end="", flush=True, file=sys.stderr)
    except InputGuardrailTripwireTriggered as e:
        print("Guardrail blocked this input:", e, file=sys.stderr, flush=True)
