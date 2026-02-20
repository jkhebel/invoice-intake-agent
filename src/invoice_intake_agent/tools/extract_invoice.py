"""Tools for extracting pdf invoices from emails."""

import warnings
import logging
from datetime import datetime
from pathlib import Path

from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError,
)
from pdfminer.high_level import extract_text

from agents import function_tool

from ..agents.invoice_agent import run_invoice_agent
from ..utils.emails import Email, load_email
from ..utils.runtime import RUNTIME
from ..utils import console as c


class InvoiceExtractionError(RuntimeError):
    """Error extracting the invoice from the email."""


def convert_doc_to_images(path):
    """Convert a document to images."""
    run_id = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = Path("outputs/artifacts/" + run_id)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    images = convert_from_path(path)

    image_paths = []
    for i, image in enumerate(images):
        image_path = output_dir / f"image_{i}.png"
        image.save(image_path)
        image_paths.append(str(image_path))

    return image_paths


def extract_text_from_doc(path):
    """Extract text from a document.

    Suppress noisy warning messages from pdfminer loggers
    (BOTH warnings and pdfminer logging).
    """

    # Suppress warning-based noise (in case the backend emits warnings).
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"Could not get FontBBox from font descriptor.*",
            category=UserWarning,
        )

        # Suppress logger-based noise from pdfminer (most common).
        logger_names = [
            "pdfminer",
            "pdfminer.pdffont",
            "pdfminer.pdfinterp",
            "pdfminer.converter",
        ]
        prev_levels = {}
        try:
            for name in logger_names:
                lg = logging.getLogger(name)
                prev_levels[name] = lg.level
                lg.setLevel(logging.ERROR)

            return extract_text(path)
        finally:
            for name, level in prev_levels.items():
                logging.getLogger(name).setLevel(level)


@function_tool
async def extract_invoice():
    """Extract the invoice from the email."""

    spinner_cm = None
    if RUNTIME.verbose:
        c.print("\n\n")
        c.rule("Invoice Specialist", style="invoice")
        c.pre("INVOICE", style="invoice")
        c.print("Analyzing email + PDF text + PDF images\n")
    else:
        c.print("\nAnalyzing email + PDF text + PDF images\n", style="dim")
        spinner_cm = c.status("[green]Running invoice specialist...")
        spinner_cm.__enter__()

    if RUNTIME.email_path is None:
        raise ValueError("Email path is not set")

    email = load_email(RUNTIME.email_path)
    pdf_path = email.get_pdf_path()

    image_paths = convert_doc_to_images(pdf_path)
    pdf_text = extract_text_from_doc(pdf_path)

    invoice_data = {
        "email": email.to_dict(),
        "pdf_text": pdf_text,
        "pdf_images": image_paths,
    }

    invoice = await run_invoice_agent(**invoice_data)

    if RUNTIME.verbose:
        c.rule("Invoice Specialist Complete", style="invoice")
        c.print("\n\n")
    else:
        if spinner_cm is not None:
            spinner_cm.__exit__(None, None, None)
            spinner_cm = None
        c.print("Invoice specialist completed.\n", style="dim")

    return invoice.model_dump()
