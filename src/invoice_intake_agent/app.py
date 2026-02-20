"""Application for the invoice intake agent."""

import sys

from agents import Runner, InputGuardrailTripwireTriggered
from openai.types.responses import ResponseTextDeltaEvent

from .utils.runtime import RUNTIME
from .utils import console as c
from .agents.orchestrator import build_orchestrator_agent


async def run_app() -> None:
    """Run the invoice intake orchestration agent with streaming output."""

    c.print("-> Assembling orchestrator agent...\n", style="dim")

    orchestrator_agent = build_orchestrator_agent()
    user_input = "Process the inbound email and its PDF attachment."

    try:
        c.print("-> Launching orchestrator agent...\n", style="dim")

        c.print("\n")
        c.rule("Orchestrator Agent", style="orch")

        # Startup spinner for any cold-start issues
        spinner_cm = c.status("[blue]Starting orchestrator agent...")
        spinner_cm.__enter__()

        result = Runner.run_streamed(orchestrator_agent, user_input, max_turns=6)

        # Verbose: stream token-by-token but only print the prefix at the start of each line.
        at_line_start = True

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                delta = event.data.delta

                # Stop the spinner as soon as we get any response
                if spinner_cm is not None:
                    spinner_cm.__exit__(None, None, None)
                    spinner_cm = None

                if not RUNTIME.verbose:
                    # Minimal mode: just stream raw deltas.
                    print(delta, end="", flush=True, file=sys.stderr)
                    continue

                # Verbose mode: stream with a prefix per line.
                for ch in delta:
                    if at_line_start:
                        c.pre("ORCHESTRATOR", style="orch")
                        at_line_start = False

                    c.print(ch, end="")

                    if ch == "\n":
                        at_line_start = True

        # Stop the spinner if it's still running
        if spinner_cm is not None:
            spinner_cm.__exit__(None, None, None)
            spinner_cm = None

        # Ensure we end with a newline in verbose mode
        if RUNTIME.verbose and not at_line_start:
            c.print("\n")

    except InputGuardrailTripwireTriggered as e:
        c.emit("ERROR", f"Guardrail blocked this input: {e}", style="err")

    if RUNTIME.verbose:
        c.rule("Orchestrator Agent Complete", style="orch")
        c.print("\n")

    c.print("-> Orchestrator agent closed.\n", style="dim")
