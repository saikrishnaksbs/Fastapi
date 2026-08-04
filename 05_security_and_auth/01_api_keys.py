"""
API KEY AUTHENTICATION
======================
This script demonstrates standard API Key authentication.
We define security dependencies to read a key from the query string or the request header.
"""

from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery

# Hardcoded valid keys for demonstration
API_KEYS = {"my-super-secret-key-123", "another-valid-key"}

# Define security scopes to extract variables
# - APIKeyQuery reads from '?api_key=...'
# - APIKeyHeader reads from 'X-API-Key: ...' header
api_key_query = APIKeyQuery(name="api_key", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Dependency function that checks if either query or header matches a valid key
def get_api_key(
    query_key: str = Security(api_key_query),
    header_key: str = Security(api_key_header),
):
    if query_key in API_KEYS:
        return query_key
    if header_key in API_KEYS:
        return header_key
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials. Invalid or missing API key."
    )

app = FastAPI(title="API Key Authentication")

# Endpoint protected by our get_api_key dependency
@app.get("/secure-resource/")
def read_secure_resource(key: str = Depends(get_api_key)):
    # Returns 200 only if 'X-API-Key' header or 'api_key' query is valid
    return {"message": "You accessed secure data!", "validated_key": key}

# To run this file:
# uvicorn 05_security_and_auth.01_api_keys:app --reload
