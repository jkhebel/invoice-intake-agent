from invoice_intake_agent.tools.extract_invoice import extract_invoice
from invoice_intake_agent.tools.emails import load_emails, Email


def test_extract_invoice():
    """Test extracting invoice."""
    email = load_emails()[0]
    invoice = extract_invoice(email)
    assert invoice is not None
    assert isinstance(invoice, dict)
