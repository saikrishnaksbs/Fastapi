"""
BODY FIELD VALIDATION AND NESTED MODELS
=======================================
This script demonstrates validation of fields in a request body model using Pydantic's `Field`.
It also covers nested Pydantic models (models referencing other models).
"""

from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI(title="Body Validation and Nested Models")

class Image(BaseModel):
    # HttpUrl guarantees that the field is a valid URL string
    url: HttpUrl
    name: str = Field(..., min_length=1, description="Descriptive name of the image")

class Item(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Folding Desk"])
    description: Optional[str] = Field(None, max_length=300)
    # Numerical validation: price must be strictly greater than 0
    price: float = Field(..., gt=0.0, description="The price must be greater than zero")
    tax: Optional[float] = Field(None, ge=0.0)
    
    # Nested field: list of image objects
    images: Optional[list[Image]] = None

@app.post("/items/")
def create_item(item: Item):
    # FastAPI automatically validates the recursive schema of the Item body.
    # If the URL inside images is invalid, it returns a 422 Unprocessable Entity error.
    return {"message": "Item created successfully", "item": item}

# To run this file:
# uvicorn 02_request_validation.02_body_validation:app --reload
