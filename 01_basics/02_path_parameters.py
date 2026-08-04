"""
PATH PARAMETERS
===============
This script demonstrates how to define path parameters (variables inside the URL).
It showcases type declarations, data validation, and route resolution ordering.
"""

from fastapi import FastAPI

app = FastAPI(title="Path Parameters")

# 1. Basic Path Parameter
# FastAPI will automatically pass the URL parameter {item_id} into the handler argument item_id
@app.get("/items/{item_id}")
def read_item(item_id: int):
    # Notice the type hint ': int'. FastAPI automatically parses the string into an integer.
    # If a user requests "/items/foo", FastAPI will reject the request with a validation error.
    return {"item_id": item_id, "type": str(type(item_id))}

# 2. Path Order Matters
# If paths overlap, FastAPI matches them in the order they are defined.
# If /users/me was defined after /users/{user_id}, requests to /users/me would match /users/{user_id} instead.
@app.get("/users/me")
def read_current_user():
    return {"user_id": "current_authenticated_user"}

@app.get("/users/{user_id}")
def read_user(user_id: str):
    return {"user_id": user_id}

# To run this file:
# uvicorn 01_basics.02_path_parameters:app --reload
