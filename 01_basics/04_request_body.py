"""
REQUEST BODY
============
This script demonstrates how to define a request body using Pydantic models.
When an endpoint expects a request body, FastAPI parses the incoming JSON,
validates the types, and populates the model object.
"""

from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Request Body")

# Define the data schema using Pydantic's BaseModel
class Product(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# Declare the schema model as a route parameter.
# Because Product inherits from BaseModel, FastAPI knows it should parse the request body as JSON.
@app.post("/products/")
def create_product(product: Product):
    product_dict = product.model_dump() # Convert the pydantic model to a dict
    if product.tax:
        price_with_tax = product.price + product.tax
        product_dict.update({"price_with_tax": price_with_tax})
    return product_dict

# To run this file:
# uvicorn 01_basics.04_request_body:app --reload
