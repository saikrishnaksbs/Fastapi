"""
PATH AND QUERY VALIDATION
=========================
This script demonstrates how to define string, numerical, and structural validations
for path and query parameters using fastapi's `Path` and `Query`.
"""

from typing import Optional
from fastapi import FastAPI, Path, Query

app = FastAPI(title="Path and Query Validation")

@app.get("/items/{item_id}")
def read_items(
    # Path parameter validation: must be an integer, greater than or equal to 1, and less than or equal to 1000
    item_id: int = Path(..., title="The ID of the item to get", ge=1, le=1000),
    
    # Query parameter validation: optional, max length of 50, matches a regex pattern, alias in URL
    q: Optional[str] = Query(
        None, 
        alias="item-query", 
        title="Search query string",
        description="Search query for matching item names.",
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_-]+$" # Alphanumeric, underscore, hyphen
    )
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

# Declaring query parameters as lists of values (e.g. ?q=foo&q=bar)
@app.get("/tags/")
def read_tags(
    q: list[str] = Query(["default_tag"], description="List of search tags")
):
    return {"tags": q}

# To run this file:
# uvicorn 02_request_validation.01_path_query_validation:app --reload
