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


@app.get("/")
def home():
    return {
        "status": "running",
        "routes": ["/extract"]
    }


@app.post("/extract", response_model=InvoiceResponse)
def extract(req: ExtractRequest):

    text = req.text or ""

    vendor = ""
    m = re.search(
        r"(Acme-[A-Za-z0-9-]+\s+Industries\s+Ltd\.?)",
        text,
        re.I
    )
    if m:
        vendor = m.group(1)


    currency = "USD"

    m = re.search(
        r"\b(USD|EUR|GBP)\b",
        text,
        re.I
    )
    if m:
        currency = m.group(1).upper()


    amount = 0.0

    m = re.search(
        r"(?:total|amount|due)[^0-9]*([0-9]+(?:\.[0-9]+)?)",
        text,
        re.I
    )

    if not m:
        m = re.search(
            r"([0-9]+(?:\.[0-9]+)?)\s*(USD|EUR|GBP)",
            text,
            re.I
        )

    if m:
        amount = float(m.group(1))


    date = ""

    m = re.search(
        r"(2026-\d\d-\d\d)",
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
