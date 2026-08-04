# Topic 09: Background Tasks & Lifespan

This module covers running asynchronous operations outside the direct request-response lifecycle and managing application setup and teardown tasks.

---

## Code Walkthrough

1. **[01_background_tasks.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/09_background_tasks_and_events/01_background_tasks.py)**
   * Shows how to register non-blocking functions with `BackgroundTasks` so the server can instantly return an HTTP success code while executing long-running calculations or sending emails in the background.
2. **[02_lifespan_events.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/09_background_tasks_and_events/02_lifespan_events.py)**
   * Explains the modern FastAPI `lifespan` handler (which replaces the deprecated `@app.on_event("startup")` and `"shutdown"` tags) using `contextlib.asynccontextmanager` to build connections or pre-load datasets.

---

## The Lifespan Protocol

```
┌───────────────────────────────────────┐
│     App Startup (Initialize DB/etc)    │  <-- Executes before serving requests
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│     App Running (Serving Endpoints)    │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│     App Shutdown (Disconnect DB/etc)   │  <-- Executes when server terminates
└───────────────────────────────────────┘
```
Using the lifespan context manager ensures resources are cleaned up properly even if the server crashes unexpectedly.
