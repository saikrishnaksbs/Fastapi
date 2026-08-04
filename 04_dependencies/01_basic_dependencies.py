"""
BASIC DEPENDENCIES
==================
This script demonstrates how to define and use simple dependencies in FastAPI.
Dependencies are functions that are called before executing the path operation function.
"""

from typing import Optional
from fastapi import FastAPI, Depends

app = FastAPI(title="Basic Dependencies")

# 1. Defining a Dependency Function
# It can accept query, path, header parameters, etc., just like a path operation function.
def common_parameters(
    q: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 100
):
    return {"q": q, "skip": skip, "limit": limit}

# 2. Injecting the Dependency
# Use `Depends` inside the endpoint handler argument.
@app.get("/items/")
def read_items(commons: dict = Depends(common_parameters)):
    # commons is populated with the dictionary returned by common_parameters()
    return {"message": "Fetching items list", "params": commons}

@app.get("/users/")
def read_users(commons: dict = Depends(common_parameters)):
    # You can reuse the exact same dependency function for multiple endpoints!
    return {"message": "Fetching users list", "params": commons}

# To run this file:
# uvicorn 04_dependencies.01_basic_dependencies:app --reload
