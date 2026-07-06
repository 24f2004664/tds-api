from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time

app = FastAPI()

LIMIT = 16
WINDOW = 10

clients = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limiter(request: Request, call_next):

    client = request.headers.get(
        "x-client-id",
        request.client.host
    )

    now = time.time()

    history = clients.get(client, [])

    history = [
        t for t in history
        if now - t < WINDOW
    ]

    if len(history) >= LIMIT:
        r = Response(
            "Too many requests",
            status_code=429
        )
        r.headers["Retry-After"] = "10"
        return r

    history.append(now)
    clients[client] = history

    return await call_next(request)



@app.get("/ping")
def ping(
    response: Response,
    request: Request
):

    rid = request.headers.get(
        "X-Request-ID"
    )

    if not rid:
        rid = str(uuid.uuid4())

    response.headers[
        "X-Request-ID"
    ] = rid

    return {
        "message": "pong",
        "request_id": rid
    }


@app.get("/")
def home():
    return {
        "status": "ok"
    }
