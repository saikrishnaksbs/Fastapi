# Topic 02: Request Validation

This module covers input constraints and validations in FastAPI, explaining how to restrict numeric limits, string patterns, list shapes, and nested data structures.

---

## Code Walkthrough

1. **[01_path_query_validation.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/02_request_validation/01_path_query_validation.py)**
   * Shows how to import and use `Path` and `Query` functions from `fastapi` to add constraints (like `gt`, `le`, `min_length`, `max_length`, `pattern`) and metadata (descriptions, titles, aliases).
2. **[02_body_validation.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/02_request_validation/02_body_validation.py)**
   * Explains Pydantic's `Field` validation for fields within a request body schema. Demonstrates nested Pydantic models (such as an object that contains a list of sub-objects).
3. **[03_extra_data.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/02_request_validation/03_extra_data.py)**
   * Shows how to configure Pydantic models to reject extra unmapped fields in incoming JSON payloads by setting `extra = "forbid"`.

---

## Key Validation Parameters

* **`min_length` / `max_length`**: Limits characters for strings.
* **`pattern`**: A regular expression string must match.
* **`gt` / `ge`**: Greater Than / Greater Than or Equal (for numbers).
* **`lt` / `le`**: Less Than / Less Than or Equal (for numbers).
* **`alias`**: Request field maps to a different internal python attribute name.
