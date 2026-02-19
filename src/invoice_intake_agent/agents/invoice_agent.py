"""Agent for extracting information from invoice images."""

import base64
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents import Agent, Runner, InputGuardrail, InputGuardrailTripwireTriggered
from openai.types.responses import ResponseTextDeltaEvent

from ..config import MODEL
from ..invoice_schema import Invoice
from .guardrails import invoice_intake_guardrail


def _image_to_data_url(image_path: str) -> str:
    """Convert an image to a data URL.
    Converts the image to a base64 encoded string (parsable by the model),
    and returns the data URL (the actual input for the model).
    This is needed because the model cannot directly process binary data,
    so base64 encoding is used to convert the image to a parsable string,
    with ASCII-safe characters.
    The data URL tells the model the data type, encoding, and payload location.
    """

    data = Path(image_path).read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _safe_get(d: dict[str, Any], keys: list[str]) -> Any:
    """Get a value from a nested dictionary safely.
    Returns None instead of raising KeyError if a key is not found.
    """
    for key in keys:
        x: Any = d  # Used to traverse the dictionary
        for key in keys:
            if isinstance(x, dict) and key in x:
                x = x[key]
            else:
                return None
    return x if isinstance(x, str) else None


def extract_invoice_one_shot(
    *,
    email: dict[str, Any],
    pdf_text: str,
    pdf_images: List[str],
) -> Invoice:
    """Single-shot: fill Invoice schema  (email + pdf text + images)"""

    # TODO: bound text size for cost control

    instructions = (
        "You extract invoice fields and return ONLY a JSON object matching "
        "the Invoice schema.\n"
        "Rules:\n"
        "- invoice_number is REQUIRED. It may only appear in the image(s); "
        "read the images carefully.\n"
        "- If a field is not present, set it to null / empty list "
        "as appropriate.\n"
        "- Prefer exact strings/numbers as printed on the invoice.\n"
        "- Dates: prefer YYYY-MM-DD if clearly implied, "
        "otherwise preserve the original date string.\n"
        "- Currency: prefer ISO 4217 codes like CAD, USD when visible.\n"
        "- Line items: include at least "
        "sku/description/quantity/unit_price/line_total when present.\n"
        "- Do not include extra keys.\n"
        "- Generate a human-readable summary of the invoice, to be used "
        "in the outbound email. This should be a bulleted list of the "
        "most important information from the invoice.\n"
    )

    invoice_agent = Agent(
        name="Invoice Specialist",
        instructions=instructions,
        model=str(MODEL),
        output_type=Invoice,
        input_guardrails=[InputGuardrail(invoice_intake_guardrail)],
    )

    subject = _safe_get(email, ["Subject"])
    body = _safe_get(email, ["Body", "Content"])

    # Construct the content for the agent to process (text + images)
    content: List[Dict[str, Any]] = [
        {
            "type": "input_text",
            "text": (
                "Extract the invoice data into the invoice schema. \n\n"
                f"Email Subject: {subject}\n"
                f"Email Body: {body}\n"
                f"PDF Text: {pdf_text}\n"
            ),
        }
    ]

    # Add the images to the content
    for image_path in pdf_images:
        content.append(
            {
                "type": "input_image",
                "image_url": _image_to_data_url(image_path),
            }
        )

    result = Runner.run_sync(
        invoice_agent,
        [{"role": "user", "content": content}],
        max_turns=1,
    )
    invoice: Invoice = result.final_output

    # TODO: supplement missing OPTIONAL fields from text/email by regex

    # Enforce Required Fields
    if invoice.invoice_number is None or not invoice.invoice_number.strip():
        raise ValueError(
            "Invoice number is required, but was not extracted."
            "Ensure you are rendering the images correctly."
        )

    return invoice
