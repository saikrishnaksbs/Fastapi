# FastAPI Learning Curriculum

This workspace is a structured, hands-on tutorial for learning and mastering **FastAPI**. Every folder represents a core module, containing an explanatory `README.md` and fully runnable code examples.

---

## Directory Index

1. **[01_basics](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/01_basics)**
   * Minimal app, Path/Query parameters, Request Bodies, mixed setups.
2. **[02_request_validation](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/02_request_validation)**
   * String/Numeric validation using `Query` and `Path`, Pydantic models & validation.
3. **[03_response_handling](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/03_response_handling)**
   * Serialization, filtering via `response_model`, status codes, HTML/Streaming/File responses.
4. **[04_dependencies](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/04_dependencies)**
   * Dependency Injection, nested dependencies, yielding cleanup resources, router/global scope.
5. **[05_security_and_auth](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/05_security_and_auth)**
   * API Key authentication, OAuth2 Password Bearer flow, hashing, and JWT authorization.
6. **[06_databases_and_orm](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/06_databases_and_orm)**
   * Integrating SQLite database with SQLModel ORM, using yield sessions for CRUD.
7. **[07_advanced_routing](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/07_advanced_routing)**
   * Modular application structuring with `APIRouter`, OpenAPI tags and customization.
8. **[08_middleware_and_cors](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/08_middleware_and_cors)**
   * CORS configuration and building custom ASGI middlewares (e.g., requests execution timers).
9. **[09_background_tasks_and_events](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/09_background_tasks_and_events)**
   * Fire-and-forget background processing and lifespan context managers (`startup`/`shutdown`).
10. **[10_websockets](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/10_websockets)**
    * Full-duplex persistent messaging, routing, and broadcasting to active clients (Chat Room).
11. **[11_testing](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/11_testing)**
    * Writing synchronous and asynchronous unit tests using `pytest` and `TestClient` / `httpx.AsyncClient`.
12. **[12_deployment_and_config](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/12_deployment_and_config)**
    * Environment configuration using `pydantic-settings`.

---

## How to Run the Code

To run any of the code examples in this curriculum, you first need to install the dependencies:

```bash
pip install fastapi uvicorn pydantic pydantic-settings sqlmodel passlib[bcrypt] python-multipart pyjwt websockets pytest httpx
```

To run a specific Python file containing a FastAPI app, execute:
```bash
uvicorn <folder_name>.<file_name_without_extension>:app --reload
```

For example, to run the hello world example:
```bash
uvicorn 01_basics.01_hello_world:app --reload
```
You can then open [http://127.0.0.1:8000](http://127.0.0.1:8000) or check the interactive documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
