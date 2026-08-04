# Topic 06: Databases & ORM (SQLModel)

This module explains how to integrate SQL relational databases (such as **SQLite**) with FastAPI using **SQLModel**.

---

## Code Walkthrough

1. **[01_sqlmodel_sqlite.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/06_databases_and_orm/01_sqlmodel_sqlite.py)**
   * Shows how to declare database models, establish SQLite connections, bootstrap the database schema tables at startup, and perform clean CRUD (Create, Read, Update, Delete) database interactions using a yield-based session dependency.

---

## Why SQLModel?

Historically, FastAPI applications used **SQLAlchemy** for database queries and **Pydantic** for HTTP request/response validation. This required duplicating fields between database models and API schemas.

**SQLModel** (created by the author of FastAPI) solves this by merging SQLAlchemy and Pydantic. A single class inherits from `SQLModel` and acts as:
* An OpenAPI-compatible request validation schema.
* An ORM class compatible with SQLAlchemy table definitions.
