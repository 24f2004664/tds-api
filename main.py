from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time

app = FastAPI()

EMAIL = "24f2004664@ds.study.iitm.ac.in"

LIMIT = 16
WINDOW = 10

clients = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Retry-After"],
)


@app.middleware("http")
async def rate_limit(request: Request, call_next):

    client_id = request.headers.get(
        "X-Client-Id",
        "default"
    )

    now = time.time()

    bucket = clients.get(client_id, [])

    bucket = [
        t for t in bucket
        if now - t < WINDOW
    ]

    if len(bucket) >= LIMIT:
        response = Response(
            status_code=429
        )
        response.headers["Retry-After"] = "10"
        return response

    bucket.append(now)
    clients[client_id] = bucket

    return await call_next(request)


@app.get("/ping")
def ping(
    request: Request,
    response: Response
):

    request_id = request.headers.get(
        "X-Request-ID"
    )

    if request_id is None:
        request_id = str(uuid.uuid4())

    response.headers[
        "X-Request-ID"
    ] = request_id

    return {
        "email": EMAIL,
        "request_id": request_id
    }


@app.get("/")
def home():
    return {
        "status": "ok"
    }
