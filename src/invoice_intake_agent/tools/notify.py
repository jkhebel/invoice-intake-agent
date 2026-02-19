"""Tools for notifying Customer Service of successful invoice intake."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from agents import function_tool

from ..invoice_schema import Invoice


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

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"outbound_email_{invoice_no}.json"

    email_payload = compose_email(invoice)

    json_path.write_text(
        json.dumps(email_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(
        f"Notification written to {json_path}",
        file=sys.stderr,
        flush=True,
    )

    return {"outbound_email_json": str(json_path)}
