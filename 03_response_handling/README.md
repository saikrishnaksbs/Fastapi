# Topic 03: Response Handling

This module details how FastAPI shapes, filters, and formats API responses, including custom status codes and diverse media formats.

---

## Code Walkthrough

1. **[01_response_model.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/03_response_handling/01_response_model.py)**
   * Shows how `response_model` on a path decorator enforces validation on the outgoing payload, filters confidential data, and handles fields that are unset or contain null defaults.
2. **[02_status_codes.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/03_response_handling/02_status_codes.py)**
   * Demonstrates setting custom success codes (e.g. `201 Created`) and raising clean HTTP errors via `HTTPException` with a custom body dictionary.
3. **[03_custom_responses.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/03_response_handling/03_custom_responses.py)**
   * Covers returning different types of HTTP payloads like HTML pages, binary files, stream chunks, or URL redirection endpoints.

---

## Serialization & Filtering
Using Pydantic with FastAPI gives us strict output boundaries. Using `response_model=UserOut` allows us to consume a database model with password hashes but serialize only public fields.
We can also fine-tune output fields using:
* `response_model_exclude_unset=True`: Omit fields not explicitly initialized.
* `response_model_exclude_none=True`: Omit fields with a value of `None`.
