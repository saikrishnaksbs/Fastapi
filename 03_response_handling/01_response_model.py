"""
RESPONSE MODEL
==============
This script demonstrates how to filter outgoing payload data using the `response_model` parameter.
It defines input schemas that include sensitive information, and response schemas that filter it out.
"""

from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Response Model")

# Input Model (what the user sends)
class UserIn(BaseModel):
    username: str
    password: str # Sensitive!
    email: EmailStr
    full_name: Optional[str] = None

# Output Model (what we return)
class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

# We specify response_model=UserOut in the path decorator.
# FastAPI will process the return value, filter out `password`, and validate against `UserOut`.
@app.post("/users/", response_model=UserOut)
def create_user(user: UserIn):
    # In a real app, you would hash the password and save to a database.
    return user

# Example of filtering out defaults/none values
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: float = 10.5

@app.get("/items/default", response_model=Item, response_model_exclude_unset=True)
def read_item_exclude_unset():
    # If we return this:
    # 'tax' has a default of 10.5 but is not set here.
    # 'description' is None.
    # Because of `response_model_exclude_unset=True`, only 'name' and 'price' are returned.
    return Item(name="Exclusive Desk", price=50.0)

# To run this file:
# uvicorn 03_response_handling.01_response_model:app --reload
