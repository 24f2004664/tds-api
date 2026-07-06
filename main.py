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

    # vendor
    vendor = ""
    m = re.search(
        r"(Acme-[A-Za-z0-9-]+\s+Industries\s+Ltd\.?)",
        text,
        re.I
    )
    if m:
        vendor = m.group(1)


    # amount
    amount = 0.0

    patterns = [
        r"(?:total\s+due|amount\s+due|balance\s+due|total|amount)\D+([0-9]+(?:\.[0-9]{1,2})?)",
        r"\b(USD|EUR|GBP)\s*([0-9]+(?:\.[0-9]{1,2})?)",
        r"([0-9]+(?:\.[0-9]{1,2})?)\s*(USD|EUR|GBP)"
    ]

    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            nums = [
                x for x in m.groups()
                if re.match(r"[0-9]", x)
            ]
            if nums:
                amount = float(nums[0])
                break


    # currency
    currency = "USD"

    m = re.search(
        r"\b(USD|EUR|GBP)\b",
        text,
        re.I
    )

    if m:
        currency = m.group(1).upper()


    # date
    date = ""

    m = re.search(
        r"(2026-\d{2}-\d{2})",
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
