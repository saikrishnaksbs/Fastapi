"""
GLOBAL AND ROUTER DEPENDENCIES
==============================
This script demonstrates registering dependencies at the application or router scope.
Instead of declaring `Depends(...)` on every single endpoint, you enforce it once for all.
"""

from fastapi import FastAPI, Depends, Header, HTTPException, status

# Dependency function that checks for a secret custom request header
def verify_secret_header(x_secret_token: str = Header(...)):
    # Requires client header 'X-Secret-Token: secret-sauce'
    if x_secret_token != "secret-sauce":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid or missing X-Secret-Token header value"
        )

# Register the dependency globally. It applies to all endpoints in this app instance.
app = FastAPI(
    title="Global Dependencies",
    dependencies=[Depends(verify_secret_header)]
)

@app.get("/secure-data/")
def get_secure_data():
    return {"message": "Authenticated via global X-Secret-Token!"}

@app.get("/other-secure-data/")
def get_other_secure_data():
    return {"message": "This endpoint is also globally protected."}

# To run this file:
# uvicorn 04_dependencies.04_global_dependencies:app --reload
