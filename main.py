from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

API_KEY = "ak_k6y590pvb5857adgly10ps41"
EMAIL = "24f2004664@ds.study.iitm.ac.in"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: List[Event]


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/analytics")
def analytics(
    body: AnalyticsRequest,
    x_api_key: str = Header(default=None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401)

    revenue = 0
    user_totals = {}

    for event in body.events:
        if event.amount > 0:
            revenue += event.amount
            user_totals[event.user] = (
                user_totals.get(event.user, 0)
                + event.amount
            )

    return {
        "email": EMAIL,
        "total_events": len(body.events),
        "unique_users": len(
            set(e.user for e in body.events)
        ),
        "revenue": revenue,
        "top_user": max(user_totals, key=user_totals.get)
    }
