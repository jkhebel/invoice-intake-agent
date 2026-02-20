# Invoice Intake Agent

A production-style invoice ingestion pipeline built using the OpenAI Agents SDK.

This application processes a local inbound email (JSON format) with a PDF attachment,
extracts structured invoice data using an AI agent, and generates a Customer Service
notification artifact.

---

## 🚀 Overview

The Invoice Intake Agent performs the following steps:

1. Loads an inbound email from a JSON file.
2. Extracts the associated PDF attachment.
3. Converts the PDF to text and images.
4. Calls a nested "Invoice Specialist" agent to extract structured invoice fields.
5. Generates a Customer Service notification file based on the extracted data.

The system supports both minimal and verbose console modes, including streaming output
and tool-level logging.

### 🤖 Agents

1. `Orchestration Agent`: Orchestrates the workflow and invokes tools.
2. `Invoice Specialist`: Parses email + PDF text + PDF extracts to a JSON Invoice.
3. `Guardrails Agent`: Reviews model inputs and flags an unwanted content.

### 🛠️ Tools

1. `extract_invoice`: loads the PDF and extracts structured data from:
    a. PDF text
    b. Any embedded image(s) in the PDF that contain important fields
    c. Returns a structured dict/JSON with extracted fields.
2. `notify` produces the outbound message to Customer Service.
    a. Drafts an outbout JSON email containing a summary and the JSON invoice.
    b. Saves the outbound email to file to downstream ingestion.

---

## 📌 Requirements

- Python 3.12+
- uv
- OpenAI API key

---

## 🧱 Project Structure

```
src/invoice_intake_agent/
├── agents/
├── tools/
├── utils/
├── app.py
├── cli.py
└── config.py
```

- **cli.py** — Command-line interface entry point
- **app.py** — Application runtime orchestration
- **agents/** — OpenAI Agents definitions
- **tools/** — Tool implementations (invoice extraction, notification)
- **utils/** — Console, runtime config, email utilities

---

## 🛠 Setup

This project uses **uv** for dependency management. Not that all **uv** commands should be run from the project root directory.

Install dependencies with:

```bash
uv sync
```

Ensure you have a valid `OPENAI_API_KEY` configured in your environment. Create a copy of the `example.env` file and resave it as `.env` in the same directory. Then, populate your API key as below:

```.env
OPENAI_API_KEY=sk-EXAMPLE1234567890
```

---

## ▶️ How to Run

Process a single email file:

```bash
uv run invoice-intake-agent path/to/email.json
```

Verbose mode (streams model output and detailed logs):

```bash
uv run invoice-intake-agent path/to/email.json -v
```

If the email references a PDF attachment, the PDF MUST exist in the same directory
as the JSON file.

---

## 🧪 Tests

To run unit testing, you'll first need to add `pytest` as a development package:

```bash
uv add pytest
```

Then run the following:

```bash
uv run pytest
```

Allow print statements in unit tests with the `-s` flag:

```bash
uv run pytest -s
```

---

## 👷🏼‍♂️ How to Build

To build to an installable `.whl` or .`.tar.gz` package, run:

```bash
uv build
```

The repo can also be installed as an executible python library:

```bash
uv pip install -e .
```

---

## 📂 Expected Input Format

The email JSON file must contain a top-level `Message` field.

Example structure:

```json
{
  "Message": {
    "Subject": "Invoice 12345",
    "Body": "Please see attached invoice.",
    "Attachments": [
      {
        "Name": "Invoice_12345.pdf",
        "ContentType": "application/pdf"
      }
    ]
  }
}
```

---

## 📄 Output Files

After execution, the following artifacts are produced:

### 1. Customer Service Notification

Located in:

```
outputs/
```

Example:

```
outputs/outbound_email_12345.json
```

If extraction fails, a placeholder notification is generated:

```
outputs/outbound_email_UNKNOWN.json
```

---

## 📄 License

This project is intended for educational and demonstration purposes.
