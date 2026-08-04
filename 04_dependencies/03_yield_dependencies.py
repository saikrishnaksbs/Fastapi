"""
DEPENDENCIES WITH YIELD
=======================
This script demonstrates dependencies that yield a resource (like a database session).
The code before the `yield` statement is executed before the endpoint handler runs.
The code after `yield` is run after the response is completed.
"""

from fastapi import FastAPI, Depends

app = FastAPI(title="Yield Dependencies")

# Simulate a database connection resource
class DatabaseConnection:
    def __init__(self):
        print("[DB] Initializing database connection...")
        self.connected = True
        
    def query(self, sql: str):
        return f"Results for query: '{sql}'"
        
    def close(self):
        print("[DB] Closing connection...")
        self.connected = False

# Dependency using yield
def get_db():
    db = DatabaseConnection()
    try:
        # FastAPI passes this database object to the handler
        yield db
    finally:
        # This runs AFTER the handler executes and the response is dispatched
        db.close()

@app.get("/data/")
def fetch_data(db: DatabaseConnection = Depends(get_db)):
    # Verify by checking application terminal prints to see setup and cleanup order
    result = db.query("SELECT * FROM users")
    return {"data": result}

# To run this file:
# uvicorn 04_dependencies.03_yield_dependencies:app --reload
