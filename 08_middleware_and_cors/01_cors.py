"""
CORS (CROSS-ORIGIN RESOURCE SHARING)
===================================
This script demonstrates how to configure CORS.
By default, web browsers block frontend scripts (like React/Vue running on localhost:3000)
from making requests to a backend on another origin (like localhost:8000).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CORS Middleware Example")

# 1. Define allowed origins.
# You can use "*" to allow everything, but listing explicit domains is recommended for security.
origins = [
    "http://localhost:3000",
    "https://example.com",
]

# 2. Add the CORSMiddleware to the app stack.
# FastAPI will intercept requests and automatically reply to preflight OPTIONS requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # List of allowed domains
    allow_credentials=True,           # Support cookies in cross-origin requests
    allow_methods=["*"],              # Allow all HTTP verbs (GET, POST, etc.)
    allow_headers=["*"],              # Allow all request headers
)

@app.get("/")
def main():
    return {"message": "CORS headers are active!"}

# To run this file:
# uvicorn 08_middleware_and_cors.01_cors:app --reload
