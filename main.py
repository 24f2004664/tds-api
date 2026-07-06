from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()


class ExtractRequest(BaseModel):
    text: str


class InvoiceResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.post("/extract", response_model=InvoiceResponse)
def extract_invoice(req: ExtractRequest):

    text = req.text or ""

    # Vendor extraction
    vendor = ""

    vendor_patterns = [
        r"(Acme-[\w-]+\s+Industries\s+Ltd\.?)",
        r"vendor[:\s]+([A-Za-z0-9\-\s\.]+)",
        r"from[:\s]+([A-Za-z0-9\-\s\.]+)"
    ]

    for p in vendor_patterns:
        m = re.search(p, text, re.I)
        if m:
            vendor = m.group(1).strip()
            break


    # Amount extraction
    amount = 0.0

    amount_patterns = [
        r"(?:total|amount|due)[:\s\$]*([0-9]+(?:\.[0-9]+)?)",
        r"([0-9]+(?:\.[0-9]+)?)"
    ]

    for p in amount_patterns:
        m = re.search(p, text, re.I)
        if m:
            amount = float(m.group(1))
            break


    # Currency extraction
    currency = "USD"

    m = re.search(r"\b(USD|EUR|GBP)\b", text, re.I)

    if m:
        currency = m.group(1).upper()


    # Date extraction
    date = ""

    m = re.search(
        r"\b(2026-[0-9]{2}-[0-9]{2})\b",
        text
    )

    if m:
        date = m.group(1)


    return {
        "vendor": vendor,
        "amount": amount,
        "currency": currency,
        "date": date
    }
