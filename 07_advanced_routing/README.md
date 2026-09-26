# Topic 07: Advanced Routing & Modular Design

This module shows how to organize a growing codebase using FastAPI's routing system and customize metadata for the Swagger UI documentation.

---

## Code Walkthrough

1. **[01_apirouter.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/07_advanced_routing/01_apirouter.py)**
   * Shows how to instantiate `APIRouter` sub-routing objects, partition endpoints into different files or logic groups, and bundle them together into the main `FastAPI` instance.
2. **[02_routing_tags.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/07_advanced_routing/02_routing_tags.py)**
   * Covers configuring endpoint metadata such as `tags`, routing summaries, inline markdown descriptions, and defining response dictionary custom schemas.
3. **[03_custom_route_decorators.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/07_advanced_routing/03_custom_route_decorators.py)**
   * Explains how custom API route decorators (like `@bik_api`) use `router.add_api_route()` internally to register routes dynamically with custom metadata like `auth_types`.

---

## Structuring Large Apps

Instead of defining 50 endpoints in one Python file, we isolate sub-resources:
```
app/
├── main.py           # Includes routers
├── routers/
│   ├── items.py      # APIRouter for /items
│   └── users.py      # APIRouter for /users
```
`APIRouter` handles prefixes, tags, and default dependencies automatically for all included endpoints.
