# Topic 11: Testing & Mocking

This module teaches you how to write unit and integration tests for your FastAPI endpoints using `pytest`.

---

## Code Walkthrough

1. **[01_testclient.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/11_testing/01_testclient.py)**
   * Outlines using the built-in `fastapi.testclient.TestClient` (backed by `httpx`) to perform synchronous requests against endpoints, verifying JSON responses, status codes, and input validation bounds.
2. **[02_async_testing.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/11_testing/02_async_testing.py)**
   * Demonstrates asynchronous endpoint testing utilizing `httpx.AsyncClient`. Includes how to override application dependencies (like databases or auth calls) during pytest runs to run tests against mock layers.

---

## Running Pytest

To run the unit tests, execute:
```bash
pytest 11_testing/01_testclient.py
pytest 11_testing/02_async_testing.py
```
FastAPI's TestClient uses HTTPX under the hood, enabling you to test routing parameters, request payloads, headers, and responses without launching a real network server.
