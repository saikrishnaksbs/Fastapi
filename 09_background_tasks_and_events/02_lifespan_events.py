"""
APPLICATION LIFESPAN EVENTS
===========================
This script demonstrates how to define startup and shutdown logic
using the modern `lifespan` parameter and `asynccontextmanager`.
This is the recommended replacement for the deprecated `@app.on_event("startup")` events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

# Global state dictionaries or database connection pools
shared_resources = {}

# Define the lifespan manager
# Code before `yield` runs on application startup.
# Code after `yield` runs on application shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    print("[LIFESPAN] Starting up application...")
    # Simulate loading model weights or establishing database connections
    shared_resources["ml_model"] = "Loaded Random Forest Model (Mock)"
    shared_resources["redis_cache"] = "Connected to Redis (Mock)"
    
    yield  # The application serves requests here
    
    # --- SHUTDOWN ---
    print("[LIFESPAN] Shutting down application...")
    # Clean up resources
    shared_resources.clear()
    print("[LIFESPAN] Cleaned up all resources.")

# Pass lifespan to the FastAPI constructor
app = FastAPI(title="Lifespan Events Example", lifespan=lifespan)

@app.get("/predict")
def predict():
    # Access resource loaded at startup
    model = shared_resources.get("ml_model", "No Model Loaded")
    return {"prediction": "Success", "using_model": model}

# To run this file:
# uvicorn 09_background_tasks_and_events.02_lifespan_events:app --reload
