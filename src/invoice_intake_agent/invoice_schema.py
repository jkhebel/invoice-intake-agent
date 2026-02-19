"""Schema for the invoice intake agent."""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class LineItem(BaseModel):
    """A line item in an invoice."""

    sku: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    line_total: Optional[float] = None
    notes: Optional[str] = None


class Invoice(BaseModel):
    """An invoice."""

    model_config = ConfigDict(extra="forbid")
    vendor_name: Optional[str] = None
    invoice_number: str = Field(
        ...,
        description="Invoice number (required; may only be present in rasterized PDF images)",
    )
    invoice_date: Optional[str] = None
    invoice_due_date: Optional[str] = None
    payment_terms: Optional[str] = None
    currency: Optional[str] = None
    customer_po_number: Optional[str] = None
    total_due: Optional[float] = None
    subtotal: Optional[float] = None
    taxes: Optional[float] = None
    taxes_breakdown: Optional[List[str]] = Field(default_factory=list)
    line_items: Optional[List[LineItem]] = Field(default_factory=list)
    ship_to_locations: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[List[str]] = Field(default_factory=list)
    summary: Optional[str] = Field(
        ...,
        description="A human-readable summary of the invoice, to be used in the outbound email. This should be a bulleted list of the most important information from the invoice.",
    )
    # TODO: expand notes (check instr.)
