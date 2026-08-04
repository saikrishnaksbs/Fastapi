"""
CUSTOM HTTP MIDDLEWARE
======================
This script demonstrates how to write a custom middleware in FastAPI
using the `@app.middleware("http")` decorator.
We will calculate the processing duration of requests and append it as a custom response header.
"""

import time
from fastapi import FastAPI, Request

app = FastAPI(title="Custom Middleware")

# Registering a custom HTTP middleware.
# The middleware takes the 'request' and a callable 'call_next' that forwards the request.
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # 1. Action BEFORE the endpoint is executed
    start_time = time.perf_counter()
    
    # 2. Forward the request to get the response
    response = await call_next(request)
    
    # 3. Action AFTER the endpoint executes
    process_time = time.perf_counter() - start_time
    
    # Add a custom header to the outgoing response object
    response.headers["X-Process-Time"] = f"{process_time:.6f} seconds"
    
    # Return the modified response
    return response

@app.get("/items/")
async def read_items():
    # Simulate a small database latency
    time.sleep(0.05)
    return {"message": "Fetched items. Check response headers for X-Process-Time!"}

# To run this file:
# uvicorn 08_middleware_and_cors.02_custom_middleware:app --reload
