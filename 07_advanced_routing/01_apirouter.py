"""
MODULAR DESIGN WITH APIROUTER
=============================
This script demonstrates how to modularize your application by splitting endpoints
into sub-routers using `APIRouter`.
"""

from fastapi import APIRouter, FastAPI

app = FastAPI(title="Modular APIRouter Application")

# 1. Defining the Users Sub-router
# We specify prefix="/users" and default tags for all endpoints in this router.
users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.get("/")
def get_users():
    # Resolves to: GET /users/
    return [{"username": "alice"}, {"username": "bob"}]

@users_router.get("/{user_id}")
def get_user(user_id: int):
    # Resolves to: GET /users/{user_id}
    return {"user_id": user_id, "username": "alice"}


# 2. Defining the Items Sub-router
items_router = APIRouter(prefix="/items", tags=["Items"])

@items_router.get("/")
def get_items():
    # Resolves to: GET /items/
    return [{"item_name": "Chair"}, {"item_name": "Table"}]


# 3. Mount/Include the Sub-routers into the Main Application
app.include_router(users_router)
app.include_router(items_router)

# Main API endpoint
@app.get("/")
def root():
    return {"message": "Welcome to our modular API!"}

# To run this file:
# uvicorn 07_advanced_routing.01_apirouter:app --reload
