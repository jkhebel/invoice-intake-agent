"""Tools for notifying Customer Service of successful invoice intake."""

import json
import sys
from pathlib import Path

from agents import function_tool

from ..utils.runtime import RUNTIME
from ..utils import console as c

from ..schema.invoice import Invoice


def compose_email(invoice: Invoice) -> dict:
    """Create a simple outbound email JSON payload."""

    invoice_no = invoice.invoice_number
    summary = invoice.summary or "(no summary provided)"
    invoice_payload = invoice.model_dump()

    content = (
        "Hello Customer Service team,\n\n"
        f"The Invoice Intake Agent has completed extraction for invoice {invoice_no}.\n\n"
        "Summary:\n"
        f"{summary}\n\n"
        "Structured invoice payload is included below.\n\n"
        "Thanks,\n"
        "Invoice Intake Agent\n"
    )

    return {
        "Message": {
            "Subject": f"Invoice Intake Agent: {invoice_no} — Please process invoice",
            "Body": {"ContentType": "Text", "Content": content},
            "From": {
                "EmailAddress": {
                    "Name": "Invoice Intake Agent",
                    "Address": "invoice.intake.agent@yourcompany.example",
                }
            },
            "ToRecipients": [
                {
                    "EmailAddress": {
                        "Name": "Customer Service",
                        "Address": "customer.service@yourcompany.example",
                    }
                }
            ],
            "CcRecipients": [],
            "Attachments": [],
            "InvoicePayload": invoice_payload,
        }
    }


@function_tool
def notify(invoice: Invoice) -> dict:
    """Write a Customer Service notification.

    The Agents SDK requires strict JSON schemas for tool inputs.
    Accepting the `Invoice` Pydantic model keeps the schema strict and avoids
    `additionalProperties` errors.

    Returns paths to the created output files.
    """

    invoice_no = invoice.invoice_number
    summary = invoice.summary or "(no summary provided)"

    spinner_cm = None
    if RUNTIME.verbose:
        c.print("\n\n")
        c.rule("Notify Customer Service", style="tool")
        c.pre("NOTIFY", style="tool")
        c.print(
            f"Preparing outbound notification for invoice {invoice_no}", style="dim"
        )
    else:
        c.print("\nRunning notification tool...\n", style="dim")
        spinner_cm = c.status("[green]Notifying Customer Service...")
        spinner_cm.__enter__()

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"outbound_email_{invoice_no}.json"

    email_payload = compose_email(invoice)

    spinner_cm = None
    if RUNTIME.verbose:
        spinner_cm = c.status("[green]Writing outbound email JSON...")
        spinner_cm.__enter__()

    json_path.write_text(
        json.dumps(email_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if spinner_cm is not None:
        spinner_cm.__exit__(None, None, None)

    if RUNTIME.verbose:
        c.ok(f"NOTIFY successfully wrote outbound email JSON to {json_path}.")
        c.pre("NOTIFY", style="tool")
        c.print(f"Summary: {summary}\n")
        c.rule("Notify Customer Service Complete", style="tool")
        c.print("\n\n")
    else:
        if spinner_cm is not None:
            spinner_cm.__exit__(None, None, None)
            spinner_cm = None
        c.print(f"Notification written to {json_path}\n", style="dim")

    return {"outbound_email_json": str(json_path)}
