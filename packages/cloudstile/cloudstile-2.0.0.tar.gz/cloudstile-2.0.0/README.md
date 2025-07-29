# `⛅` Cloudstile
An unofficial Cloudflare Turnstile library with both asynchronous and synchronous support out of the box.

You can find more documentation on how to use Cloudstile in our [examples](https://github.com/notaussie/cloudstile/tree/main/examples) or our [wiki](https://github.com/notaussie/cloudstile/wiki).

[![codecov](https://codecov.io/github/NotAussie/cloudstile/graph/badge.svg?token=6VKWB9GXEU)](https://codecov.io/github/NotAussie/cloudstile)

## `📥` Installation
**Cloudstile** is available for download via PyPI. To install it, simply do:
```shell
pip install cloudstile
```

## `🎭` Example

Here are some basic examples of how to validate a user's turnstile token.

> [!WARNING]
> These examples expect the user's IP to be transparent. If you're using something like Cloudflare's proxy service, then you'll need to access the corresponding header for your use case.

### `🍷` Quart *(Asynchronous)*

```python
from quart import Quart, request, jsonify
from cloudstile import AsyncTurnstile

app = Quart(__name__)
turnstile = AsyncTurnstile(token="...")

@app.route("/submit", methods=["POST"])
async def submit():

    body = await request.form

    response = await turnstile.validate(
        body.get("cf-turnstile-response", "..."),
        request.remote_addr,
    )

    return jsonify(response.model_dump()) # <- Response is a pydantic object

```

### `🏃‍♀️` FastAPI *(Asynchronous)*

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from cloudstile import AsyncTurnstile

app = FastAPI()
turnstile = AsyncTurnstile(token="...")

@app.post("/submit")
async def submit(request: Request):

    body = await request.form()

    response = await turnstile.validate(
        body.get("cf-turnstile-response", "..."),
        request.client.host,
    )

    return JSONResponse(response.model_dump()) # <- Response is a pydantic object

```


### `🦥` Flask *(Synchronous)*

```python
from flask import Flask, request, jsonify
from cloudstile import SyncTurnstile

app = Flask(__name__)
turnstile = SyncTurnstile(token="...")

@app.route("/submit", methods=["POST"])
def submit():

    body = request.form

    response = turnstile.validate(
        body.get("cf-turnstile-response", "..."),
        request.remote_addr,
    )

    return jsonify(response.model_dump()) # <- Response is a pydantic object

```
