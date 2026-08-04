# Topic 04: Dependency Injection

This module explores FastAPI's built-in **Dependency Injection** system, explaining how dependencies are declared, nested, reused, and run with startup and teardown lifecycles.

---

## Code Walkthrough

1. **[01_basic_dependencies.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/04_dependencies/01_basic_dependencies.py)**
   * Outlines simple functional dependencies with `Depends` to extract common query variables and share routing parameters.
2. **[02_sub_dependencies.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/04_dependencies/02_sub_dependencies.py)**
   * Explains nested hierarchies where dependencies depend on other dependencies, showcasing parameter inheritance.
3. **[03_yield_dependencies.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/04_dependencies/03_yield_dependencies.py)**
   * Shows how to use `yield` instead of `return`. This allows dependencies to perform teardown actions (e.g. closing database sessions) after HTTP responses are dispatched.
4. **[04_global_dependencies.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/04_dependencies/04_global_dependencies.py)**
   * Covers registering dependencies globally across the entire app instance or routing modules, rather than defining them endpoint-by-endpoint.

---

## Key Concepts

### Dependency Injection
Dependency Injection (DI) allows a program to provide objects, parameters, or configurations automatically without the endpoint needing to instantiate them manually. This is critical for:
* Reusing logic (e.g., parsing authorization headers).
* Managing database sessions cleanly.
* Mocking components during test suites.
