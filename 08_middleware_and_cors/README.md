# Topic 08: Middleware & CORS

This module explains how to configure security origins (CORS) and write custom middleware handlers to execute code before requests hit endpoints, or after endpoints produce responses.

---

## Code Walkthrough

1. **[01_cors.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/08_middleware_and_cors/01_cors.py)**
   * Details utilizing the `CORSMiddleware` utility from `fastapi.middleware.cors` to configure origin domains, headers, credentials, and allowed HTTP method verbs.
2. **[02_custom_middleware.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/08_middleware_and_cors/02_custom_middleware.py)**
   * Shows how to construct custom ASGI/HTTP middleware by intercepting the `request` pipeline to audit system diagnostics (e.g., adding an execution time header `X-Process-Time` to outgoing responses).

---

## What is Middleware?

Middleware is a function that runs before every request is processed by any specific path operation. It also runs after the path operation produces a response.
* It can modify incoming request headers or contents.
* It can halt execution (e.g., returning a custom response directly).
* It can modify outgoing responses (e.g., appending security headers).
