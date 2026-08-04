"""
ENVIRONMENT CONFIGURATION WITH PYDANTIC-SETTINGS
================================================
This script demonstrates how to load environment configurations from a `.env` file
and environment variables using `pydantic-settings`.
"""

from typing import Optional
from functools import lru_cache
from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. Define the Settings Model
# Pydantic Settings reads variables from environment variables (case-insensitive)
# and falls back to values defined in `.env` or class defaults.
class Settings(BaseSettings):
    # Configure Pydantic V2 settings to read from a local .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "FastAPI Classroom Application"
    admin_email: str = "admin@example.com"
    database_url: str = "sqlite:///./prod_db.db"
    
    # Optional field that requires no value
    api_key_secret: Optional[str] = None
    
    # Port configuration defaults to integer 8000
    app_port: int = 8000

# 2. Use LRU Cache to load settings once
# This avoids re-reading the filesystem on every request.
@lru_cache
def get_settings():
    return Settings()

app = FastAPI(title="Pydantic Settings Example")

# 3. Inject Settings via Depends
@app.get("/info")
def get_info(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "database_url": settings.database_url,
        "api_key_secret_configured": settings.api_key_secret is not None
    }

# To run this file:
# 1. Optionally create a file named `.env` in this directory containing:
#    DATABASE_URL=sqlite:///./custom_db.db
#    API_KEY_SECRET=xyz789
# 2. Run uvicorn:
#    uvicorn 12_deployment_and_config.01_pydantic_settings:app --reload
