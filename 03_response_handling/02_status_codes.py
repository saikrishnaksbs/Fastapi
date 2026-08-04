"""
STATUS CODES AND EXCEPTIONS
===========================
This script demonstrates how to set explicit HTTP status codes for success responses
and how to raise exceptions with client-friendly HTTP error messages.
"""

from fastapi import FastAPI, HTTPException, status

app = FastAPI(title="Status Codes and Exceptions")

# Hardcoded user database for simulation
database = {"admin": "secret_pass"}

# 1. Custom Success Status Code
# Use `status_code` in the decorator. status.HTTP_201_CREATED resolves to 201.
@app.post("/items/", status_code=status.HTTP_201_CREATED)
def create_item(name: str):
    return {"message": f"Item '{name}' successfully created"}

# 2. Raising HTTPException
# If a condition is not met, raise an HTTPException with an HTTP status code (e.g. 404, 400).
@app.get("/users/{username}")
def read_user(username: str):
    if username not in database:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' was not found in the database."
        )
    return {"username": username}

# To run this file:
# uvicorn 03_response_handling.02_status_codes:app --reload
