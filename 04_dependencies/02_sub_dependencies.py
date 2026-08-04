"""
SUB-DEPENDENCIES
================
This script demonstrates how dependencies can depend on other dependencies.
FastAPI automatically resolves the dependency tree.
"""

from typing import Optional
from fastapi import FastAPI, Depends, Cookie

app = FastAPI(title="Sub-Dependencies")

# First-level dependency: extract query parameter
def query_extractor(q: Optional[str] = None):
    return q

# Second-level dependency (Sub-dependency):
# It depends on `query_extractor` and reads a cookie value.
def query_or_cookie_extractor(
    q: Optional[str] = Depends(query_extractor),
    last_query: Optional[str] = Cookie(None)
):
    # If a query is provided, use it; otherwise, fall back to the cookie
    if not q:
        return last_query
    return q

@app.get("/items/")
def read_query(query_value: Optional[str] = Depends(query_or_cookie_extractor)):
    # FastAPI resolves query_extractor first, passes its output to query_or_cookie_extractor,
    # and then yields the final value to this endpoint.
    return {"query_resolved": query_value}

# To run this file:
# uvicorn 04_dependencies.02_sub_dependencies:app --reload
