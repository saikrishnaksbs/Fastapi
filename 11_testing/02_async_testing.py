"""
ASYNCHRONOUS TESTING AND DEPENDENCY OVERRIDES
=============================================
This script demonstrates how to write async tests using `httpx.AsyncClient`.
It also shows how to override endpoint dependencies for mock assertions.
"""

import pytest
from fastapi import FastAPI, Depends
from httpx import ASGITransport, AsyncClient

# 1. Define target API
app = FastAPI(title="Async Testing Target")

# Dependency we want to mock during testing
def get_user_status():
    # In production, this might call a database or an external auth server
    return "active_member"

@app.get("/premium-content")
def get_premium(status: str = Depends(get_user_status)):
    if status != "premium_member":
        return {"access": "denied", "reason": "Requires premium status"}
    return {"access": "granted", "content": "Exclusive Premium Video"}


# 2. Dependency Overriding for tests
# We can swap the implementation by modifying `app.dependency_overrides`.
def mock_premium_status():
    return "premium_member"


# 3. Async Test Cases (using pytest-asyncio or standard async test runs)
@pytest.mark.asyncio
async def test_premium_denied_by_default():
    # Test client using ASGITransport for async mock requests
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/premium-content")
        assert response.status_code == 200
        assert response.json()["access"] == "denied"

@pytest.mark.asyncio
async def test_premium_granted_with_override():
    # Override the dependency for this test case
    app.dependency_overrides[get_user_status] = mock_premium_status
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/premium-content")
            assert response.status_code == 200
            assert response.json()["access"] == "granted"
            assert response.json()["content"] == "Exclusive Premium Video"
    finally:
        # Clean up overrides after the test is complete
        app.dependency_overrides.clear()

# To run tests:
# pytest 11_testing/02_async_testing.py
