"""Agent for extracting information from invoice images."""

import base64

from pathlib import Path
from typing import Any, Dict, List

from agents import Agent, Runner, InputGuardrail
from openai.types.responses import ResponseTextDeltaEvent

from ..config import MODEL
from ..invoice_schema import Invoice
from .guardrails import invoice_intake_guardrail

from ..utils.runtime import RUNTIME
from ..utils import console as c


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


# TODO: move to utils
def _safe_get(d: dict[str, Any], keys: list[str]) -> Any:
    """Get a value from a nested dictionary safely.
    Returns None instead of raising KeyError if a key is not found.
    """
    x: Any = d  # Used to traverse the dictionary
    for k in keys:
        if isinstance(x, dict) and k in x:
            x = x[k]
        else:
            return None
    return x


async def run_invoice_agent(
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

    subject = _safe_get(email, ["Subject"]) or ""
    body = _safe_get(email, ["Body", "Content"]) or ""

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

    messages = [{"role": "user", "content": content}]

    result = Runner.run_streamed(
        invoice_agent,
        messages,
        max_turns=1,
    )

    spinner_cm = None
    if RUNTIME.verbose:
        spinner_cm = c.status(
            "[green]Invoice Specialist analyzing email + PDF text + PDF images..."
        )
        spinner_cm.__enter__()

        at_line_start = True
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                for ch in event.data.delta:
                    if spinner_cm is not None:
                        spinner_cm.__exit__(None, None, None)
                        spinner_cm = None
                    if at_line_start:
                        c.pre("INVOICE_AGENT", style="invoice")
                        at_line_start = False
                    c.print(ch, style="dim", end="")
                    if ch == "\n":
                        at_line_start = True
        if spinner_cm is not None:
            spinner_cm.__exit__(None, None, None)
            spinner_cm = None
        if not at_line_start:
            c.print("\n")
    else:
        # Minimal mode: just stream raw deltas.
        async for _ in result.stream_events():
            pass
        if spinner_cm is not None:
            spinner_cm.__exit__(None, None, None)
            spinner_cm = None

    invoice: Invoice = result.final_output

    # TODO: supplement missing OPTIONAL fields from text/email by regex

    # Enforce Required Fields
    if not invoice.invoice_number or not invoice.invoice_number.strip():
        if RUNTIME.verbose:
            c.error("INVOICE_AGENT failed to extract invoice number.")
            c.rule("Invoice Specialist Error")
            c.print("\n\n")
        raise ValueError(
            "Invoice number is required, but was not extracted."
            "Ensure you are rendering the images correctly."
        )
    if RUNTIME.verbose:
        c.ok("INVOICE_AGENT successfully extracted invoice number.")

    return invoice
