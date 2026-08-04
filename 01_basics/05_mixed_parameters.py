"""
MIXED PARAMETERS
================
This script demonstrates combining path, query, and request body parameters in a single route.
FastAPI is smart enough to recognize which is which.
"""

from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Mixed Parameters")

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

# In the handler signature:
# - 'item_id' matches the URL path parameter -> Path parameter.
# - 'item' is a Pydantic model -> Request body.
# - 'q' is a standard scalar type -> Query parameter.
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, q: Optional[str] = None):
    result = {"item_id": item_id, "item": item}
    if q:
        result.update({"q": q})
    return result

# To run this file:
# uvicorn 01_basics.05_mixed_parameters:app --reload
