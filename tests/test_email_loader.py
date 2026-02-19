from invoice_intake_agent.tools.emails import load_emails, Email


def test_load_emails():
    """Test loading emails."""
    emails = load_emails()
    assert len(emails) > 0
    email = emails[0]
    assert isinstance(email, Email)
    print(email)
