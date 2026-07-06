from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

API_KEY = "ak_k6y590pvb5857adgly10ps41"
EMAIL = "YOUR_EMAIL_HERE"   # replace with your logged-in email

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Event(BaseModel):
    user: str
    amount: float
    ts: int

class Request(BaseModel):
    events: List[Event]


@app.post("/analytics")
def analytics(
    data: Request,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    events = data.events

    totals = {}

    revenue = 0

    for e in events:
        if e.amount > 0:
            revenue += e.amount
            totals[e.user] = totals.get(e.user, 0) + e.amount

    top_user = max(totals, key=totals.get) if totals else ""

    return {
        "email": EMAIL,
        "total_events": len(events),
        "unique_users": len(set(e.user for e in events)),
        "revenue": revenue,
        "top_user": top_user
    }
