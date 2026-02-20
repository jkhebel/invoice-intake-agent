"""Orchestration agent for ingesting invoices from emails."""

from __future__ import annotations

import asyncio
import sys

from agents import Agent, Runner, InputGuardrail, InputGuardrailTripwireTriggered
from openai.types.responses import ResponseTextDeltaEvent

from ..config import MODEL
from .guardrails import invoice_intake_guardrail
from ..tools.extract_invoice import extract_invoice
from ..tools.notify import notify


def build_orchestrator_agent() -> Agent:
    """Build the pipeline for the invoice intake agent."""

    instructions = (
        "You are an orchestration agent for an invoice-intake pipeline.\n"
        "Your job is to:\n"
        "1) Call extract_invoice() exactly once to extract structured "
        "invoice fields from the inbound email + its PDF "
        "(including reading key fields from images).\n"
        "2) Then call notify() exactly once with the full extracted invoice "
        "to write a Customer Service notification "
        "(human summary + JSON payload) to the outputs folder.\n"
        "Rules:\n"
        "- Announce when you are calling any tools.\n"
        "- Do not ask the user any questions.\n"
        "- Do not loop or retry tools.\n"
        "- After notify() print a short confirmation with the output file path"
        " returned by notify(), followed by the invoice'shuman summary.\n"
        "- Start a new line for each tool call."
    )

    return Agent(
        name="Invoice Intake Agent",
        model=str(MODEL),
        instructions=instructions,
        tools=[extract_invoice, notify],
        input_guardrails=[InputGuardrail(invoice_intake_guardrail)],
    )
