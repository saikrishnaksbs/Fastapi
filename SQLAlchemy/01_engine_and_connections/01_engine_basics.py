"""
01. ENGINE AND CONNECTION BASICS (SQLAlchemy 2.0)
==================================================
This script demonstrates the low-level Core fundamentals of SQLAlchemy 2.0:
1. Creating an Engine (`create_engine`).
2. Configuring Connection Pools (`pool_size`, `max_overflow`).
3. Executing raw SQL statements using `text()`.
4. Parameter binding for preventing SQL injection.
5. Explicit transaction handling with `engine.connect()` vs `engine.begin()`.
"""

from sqlalchemy import create_engine, text

# 1. Creating an Engine
# The Engine is the starting point for any SQLAlchemy application.
# It manages the connection pool and dialect to translate Python code to database-specific SQL.
DATABASE_URL = "sqlite:///:memory:"  # In-memory SQLite database for testing

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to True to log all emitted SQL statements to stderr
    # Connection pool options (for DBs like PostgreSQL/MySQL):
    # pool_size=5,       # Number of persistent database connections to keep
    # max_overflow=10,   # Extra connections allowed beyond pool_size during bursts
)

def demo_raw_sql_execution():
    print("\n--- 1. Executing Raw SQL with text() ---")
    # `engine.connect()` opens a connection from the pool.
    # By default, connection requires manual commits unless using `engine.begin()`.
    with engine.connect() as conn:
        # Create a table using text()
        conn.execute(
            text(
                "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
            )
        )
        conn.commit()  # Explicit commit required when using connect()

        # Insert data with parameter binding (NEVER string format variables into SQL!)
        conn.execute(
            text("INSERT INTO users (name, email) VALUES (:name, :email)"),
            [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
            ],
        )
        conn.commit()

        # Query data back
        result = conn.execute(text("SELECT id, name, email FROM users"))
        # Result contains Row objects which can be accessed by index, name, or unpacking
        for row in result:
            print(f"User #{row.id}: {row.name} <{row.email}>")

def demo_transactional_context():
    print("\n--- 2. Automatic Transaction Context with engine.begin() ---")
    # `engine.begin()` opens a connection AND starts a transaction.
    # It automatically COMMITs if the block finishes without error, or ROLLBACKs on exception.
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO users (name, email) VALUES (:name, :email)"),
            {"name": "Charlie", "email": "charlie@example.com"},
        )
        # No explicit conn.commit() needed here! Auto-committed at end of block.

    # Verify Charlie was inserted
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT name FROM users WHERE name = :name"),
            {"name": "Charlie"},
        )
        user = result.scalar()  # Fetches single first-column scalar value
        print(f"Fetched via scalar(): {user}")

if __name__ == "__main__":
    demo_raw_sql_execution()
    demo_transactional_context()
