"""
HELLO WORLD
===========
This script demonstrates the simplest FastAPI application.
It sets up a FastAPI instance and registers a root path GET endpoint.
"""

from fastapi import FastAPI

# Create the FastAPI application instance
app = FastAPI(title="FastAPI Hello World")

# Decorators (e.g. @app.get) register routes with specific HTTP methods and paths
@app.get("/")
def read_root():
    # Returning a standard Python dictionary or list automatically converts to JSON response
    return {"message": "Hello, World!"}

# To run this file:
# uvicorn 01_basics.01_hello_world:app --reload
