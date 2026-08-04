"""
FORBIDDING EXTRA DATA IN PYDANTIC
=================================
By default, Pydantic ignores extra properties passed to a request body.
This script shows how to enforce a strict policy where extra fields cause validation failures.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict

app = FastAPI(title="Forbidding Extra Data")

class StrictUser(BaseModel):
    # Using Pydantic V2 ConfigDict to forbid extra fields
    model_config = ConfigDict(extra="forbid")
    
    username: str = Field(..., min_length=3)
    email: str

@app.post("/users/")
def create_user(user: StrictUser):
    # If the client sends {"username": "alice", "email": "alice@eg.com", "admin": true},
    # FastAPI will reject with a 422 validation error due to 'admin' being an extra field.
    return user

# To run this file:
# uvicorn 02_request_validation.03_extra_data:app --reload
