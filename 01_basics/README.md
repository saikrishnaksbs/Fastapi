# Topic 01: Basics & Routing

This module covers the core building blocks of any FastAPI application: setting up an app, launching a local development server, and handling HTTP requests using path parameters, query parameters, and request bodies.

---

## Code Walkthrough

1. **[01_hello_world.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/01_basics/01_hello_world.py)**
   * Demonstrates how to instantiate the `FastAPI` application class and declare a simple `GET` route handler. It covers how FastAPI handles JSON responses automatically when you return a dictionary or a list.
2. **[02_path_parameters.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/01_basics/02_path_parameters.py)**
   * Details how path parameters are mapped from URL paths directly to endpoint function arguments. Explains type conversion (e.g. string to integer) and path-based routing priority (ordering routes).
3. **[03_query_parameters.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/01_basics/03_query_parameters.py)**
   * Explains parameters that appear after the `?` in URL query strings. Includes configuring default parameters, optional parameter fields, and casting them to Python boolean values.
4. **[04_request_body.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/01_basics/04_request_body.py)**
   * Introduces using **Pydantic** models to define custom JSON request payload schemas. FastAPI parses incoming JSON data, validates it against schemas, and passes it as object attributes.
5. **[05_mixed_parameters.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/01_basics/05_mixed_parameters.py)**
   * Combines all parameter types in a single endpoint handler, showing how FastAPI intelligently distinguishes path parameters, query parameters, and request body structures.

---

## Concepts

### Uvicorn and ASGI
FastAPI applications are asynchronous and adhere to the **ASGI** (Asynchronous Server Gateway Interface) standard. A server like **Uvicorn** is needed to load and serve your application.

### Automatic Swagger UI
FastAPI automatically parses your endpoint code and parameters to generate Interactive Documentation.
* Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc UI: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
