from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------
# Type conversion
# --------------------------

def convert(key, value):

    if key in ["port", "workers"]:
        return int(value)

    if key == "debug":
        return str(value).lower() in [
            "true",
            "1",
            "yes",
            "on"
        ]

    return str(value)



@app.get("/effective-config")
def effective_config(
    set: List[str] = Query(default=[])
):

    # 1. defaults
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000"
    }


    # 2. config.development.yaml
    # empty, no changes


    # 3. .env layer
    dotenv = {
        "APP_PORT": "8201",
        "NUM_WORKERS": "14",
        "APP_API_KEY": "key-kl9vnhqop0"
    }

    for k, v in dotenv.items():

        if k == "NUM_WORKERS":
            key = "workers"

        elif k.startswith("APP_"):
            key = (
                k[4:]
                .lower()
            )

        else:
            continue

        config[key] = convert(
            key,
            v
        )


    # 4. OS env APP_* layer
    os_env = {
        "APP_WORKERS": os.getenv(
            "APP_WORKERS",
            "5"
        ),
        "APP_LOG_LEVEL": os.getenv(
            "APP_LOG_LEVEL",
            "debug"
        )
    }

    for k, v in os_env.items():

        key = (
            k[4:]
            .lower()
        )

        config[key] = convert(
            key,
            v
        )


    # 5. CLI query overrides
    for item in set:

        if "=" in item:

            key, value = item.split(
                "=",
                1
            )

            config[key] = convert(
                key,
                value
            )


    # mask secret
    config["api_key"] = "****"


    return config


@app.get("/")
def home():
    return {
        "status": "running"
    }
