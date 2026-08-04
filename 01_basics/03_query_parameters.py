"""
QUERY PARAMETERS
================
This script demonstrates query parameters.
Any handler arguments that are not part of the path parameters are interpreted as query parameters.
"""

from typing import Optional
from fastapi import FastAPI

app = FastAPI(title="Query Parameters")

# Query parameters can have default values, be optional (via typing.Optional or None),
# or be required (by leaving out default values).
@app.get("/items/")
def read_items(
    skip: int = 0,               # Defaults to 0 if not provided
    limit: int = 10,             # Defaults to 10 if not provided
    search: Optional[str] = None # Optional string parameter
):
    # FastAPI handles boolean conversions automatically if typed as bool (e.g. "yes", "true", "1" -> True)
    return {
        "skip": skip,
        "limit": limit,
        "search": search,
    }

# Defining a query parameter as required: simply omit the default value.
@app.get("/users/")
def read_users(required_param: str):
    return {"required_param": required_param}

# To run this file:
# uvicorn 01_basics.03_query_parameters:app --reload
