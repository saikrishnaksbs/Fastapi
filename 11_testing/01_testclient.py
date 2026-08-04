"""
SYNCHRONOUS TESTING WITH TESTCLIENT
===================================
This script contains a self-contained FastAPI application and pytest test cases.
It demonstrates using TestClient to execute mock requests and assert response states.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

# 1. Define target API for testing
app = FastAPI(title="Testing Target App")

@app.get("/items/{item_id}")
def read_item(item_id: str):
    if item_id == "forbidden":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not allowed to access this item"
        )
    return {"item_id": item_id, "name": f"Item {item_id}"}

@app.post("/items/")
def create_item(item: dict):
    return {"message": "Created", "item": item}


# 2. Instantiate TestClient
client = TestClient(app)


# 3. Test Cases (runnable with `pytest`)
def test_read_item():
    response = client.get("/items/portal-gun")
    assert response.status_code == 200
    assert response.json() == {"item_id": "portal-gun", "name": "Item portal-gun"}

def test_read_item_forbidden():
    response = client.get("/items/forbidden")
    assert response.status_code == 403
    assert response.json()["detail"] == "You are not allowed to access this item"

def test_create_item():
    payload = {"name": "Screwdriver", "quantity": 5}
    response = client.post("/items/", json=payload)
    assert response.status_code == 200
    assert response.json()["item"] == payload

# To run tests:
# pytest 11_testing/01_testclient.py
