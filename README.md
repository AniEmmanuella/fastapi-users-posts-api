# Users and Posts API

A typed REST API built with FastAPI and Pydantic. Inputs, outputs and failures follow a documented contract, and the OpenAPI docs are generated automatically.

## Demo

Demo recording: DEMO_LINK_HERE

## Endpoints

| Method | Path | Success | Errors |
|--------|------|---------|--------|
| POST | /users | 201 | 409 duplicate, 422 invalid |
| GET | /users | 200 | |
| GET | /users/{user_id} | 200 | 404 |
| DELETE | /users/{user_id} | 204 | 404 |
| POST | /users/{user_id}/posts | 201 | 404, 422 |
| GET | /posts | 200 | |

## Error contract

- 404 and 409 return `{"detail": "<message>"}`
- 422 returns a list of validation errors, each with `loc` and `msg`

## Setup

    python -m venv .venv
    .\.venv\Scripts\python -m pip install -r requirements.txt

## Run

    .\.venv\Scripts\python -m uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs for the interactive documentation.

## Test

    .\.venv\Scripts\python -m pytest -v
