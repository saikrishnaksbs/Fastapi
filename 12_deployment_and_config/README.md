# Topic 12: Deployment Configuration

This module covers best practices for configuring application variables, keys, and environment toggles.

---

## Code Walkthrough

1. **[01_pydantic_settings.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/12_deployment_and_config/01_pydantic_settings.py)**
   * Shows how to utilize `pydantic-settings` to declare a structured `Settings` class that automatically reads environment variables or loads configurations from a `.env` configuration file, applying schema verification to application configs.

---

## Configuration Best Practices

According to the Twelve-Factor App methodology, configuration variables must be isolated from code:
* Avoid committing passwords, API secrets, or port overrides into git repositories.
* Use environment variables or local `.env` files.
* Leveraging `BaseSettings` from `pydantic-settings` verifies that required settings exist and matches their types before loading the application.
