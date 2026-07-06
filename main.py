from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import uuid
import base64

app = FastAPI()

TOTAL_ORDERS = 51
RATE_LIMIT = 20
WINDOW = 10


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Storage
# -------------------------

idempotency_store = {}

created_orders = {}

rate_buckets = {}


catalog = [
    {
        "id": i,
        "name": f"order-{i}"
    }
    for i in range(1, TOTAL_ORDERS + 1)
]


# -------------------------
# Models
# -------------------------

class OrderRequest(BaseModel):
    item: str | None = None


# -------------------------
# Rate limit middleware
# -------------------------

@app.middleware("http")
async def rate_limit(request, call_next):

    client = request.headers.get(
        "x-client-id"
    )

    if client:

        now = time.time()

        bucket = rate_buckets.get(
            client,
            []
        )

        bucket = [
            t for t in bucket
            if now - t < WINDOW
        ]

        if len(bucket) >= RATE_LIMIT:
            response = Response(
                "Rate limit exceeded",
                status_code=429
            )
            response.headers["Retry-After"] = "10"
            return response

        bucket.append(now)

        rate_buckets[client] = bucket


    return await call_next(request)



# -------------------------
# Idempotent POST
# -------------------------

@app.post("/orders", status_code=201)
def create_order(
    body: OrderRequest = None,
    idempotency_key: str = Header(None)
):

    if not idempotency_key:
        raise HTTPException(
            status_code=400
        )

    if idempotency_key in idempotency_store:
        return idempotency_store[idempotency_key]


    order = {
        "id": str(uuid.uuid4()),
        "item": body.item if body else None
    }

    idempotency_store[idempotency_key] = order

    return order



# -------------------------
# Pagination
# -------------------------

@app.get("/orders")
def list_orders(
    limit: int = 10,
    cursor: str | None = None
):

    start = 0

    if cursor:
        start = int(
            base64.b64decode(
                cursor.encode()
            ).decode()
        )


    end = min(
        start + limit,
        TOTAL_ORDERS
    )


    next_cursor = None

    if end < TOTAL_ORDERS:
        next_cursor = (
            base64.b64encode(
                str(end).encode()
            )
            .decode()
        )


    return {
        "items": catalog[start:end],
        "next_cursor": next_cursor
    }



@app.get("/")
def home():
    return {
        "status": "running"
    }
