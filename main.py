from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid

app = FastAPI()

EMAIL = "24f2004664@ds.study.iitm.ac.in"

ALLOWED_ORIGIN = "https://dash-yo1kg6.example.com"


# Strict CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        ALLOWED_ORIGIN
    ],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


# Required headers middleware
@app.middleware("http")
async def add_headers(request: Request, call_next):

    start = time.time()

    response = await call_next(request)

    duration = time.time() - start

    response.headers[
        "X-Request-ID"
    ] = str(uuid.uuid4())

    response.headers[
        "X-Process-Time"
    ] = str(duration)

    return response


@app.get("/stats")
def stats(values: str):

    nums = [
        int(x)
        for x in values.split(",")
        if x.strip()
    ]

    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums)
    }


@app.get("/")
def home():
    return {
        "status": "running"
    }
