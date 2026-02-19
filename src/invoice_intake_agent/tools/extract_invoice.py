"""Tools for extracting pdf invoices from emails."""

import sys
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

from ..agents.invoice_agent import extract_invoice_one_shot
from ..tools.emails import Email, load_emails


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
def extract_invoice():
    """Extract the invoice from the email."""

    email = load_emails()[0]
    pdf_path = email.get_pdf_path()
    image_paths = convert_doc_to_images(pdf_path)
    pdf_text = extract_text_from_doc(pdf_path)

    invoice_data = {
        "email": email.to_dict(),
        "pdf_text": pdf_text,
        "pdf_images": image_paths,
    }

    invoice = extract_invoice_one_shot(**invoice_data)
    return invoice.model_dump()
