"""
CUSTOM ROUTE DECORATORS & DYNAMIC ROUTE REGISTRATION
=====================================================
This script demonstrates how custom route decorators (like `@bik_api`)
handle Path Parameters, Query Parameters, and Request Bodies in FastAPI.

Key Takeaways:
1. FastAPI inspects the decorated function's signature (`def handler(...)`).
2. Parameters matching `{var}` in `api_name` -> Path Parameters.
3. Parameters typed with Pydantic `BaseModel` -> Request Body.
4. Scalar parameters not in `api_name` -> Query Parameters.
5. If wrapping the handler (`def wrapper(...)`), MUST use `@wraps(func)` from `functools`
   so FastAPI can read the parameter annotations.
"""

from enum import Enum
from functools import wraps
from typing import Callable, List, Optional
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

# Initialize App & Router
app = FastAPI(title="Custom Route Decorators Demo")
router = APIRouter()


# 1. Define Enum & Models
class AuthTypes(str, Enum):
    PUBLIC = "PUBLIC"
    AUTHENTICATED = "AUTHENTICATED"
    ADMIN = "ADMIN"


class EventPayload(BaseModel):
    event_type: str
    channel_id: str
    message: str


# 2. Custom API Decorator Implementation
def bik_api(
    api_name: str,
    methods: Optional[List[str]] = None,
    auth_types: Optional[List[AuthTypes]] = None,
    router: APIRouter = router,
    tags: Optional[List[str]] = None,
):
    """
    A custom route decorator that registers an endpoint using `router.add_api_route()`.
    Demonstrates intercepting Path, Query, and Body parameters.
    """
    if methods is None:
        methods = ["GET"]
    if auth_types is None:
        auth_types = [AuthTypes.PUBLIC]

    def decorator(func: Callable) -> Callable:
        # Using @wraps(func) preserves function metadata & annotations for FastAPI
        @wraps(func)
        def wrapper(*args, **kwargs):
            # kwargs contains all resolved path params, query params, and body payload!
            print(f"[DECORATOR LOG] Request to '{api_name}' | Params: {kwargs}")
            return func(*args, **kwargs)

        # Register the wrapped function dynamically using router.add_api_route()
        router.add_api_route(
            path=api_name,
            endpoint=wrapper,
            methods=methods,
            tags=tags or ["Custom Decorator APIs"],
            name=func.__name__,
        )

        # Attach custom metadata to function for runtime auth checks
        wrapper.__auth_types__ = auth_types
        wrapper.__api_name__ = api_name

        return wrapper

    return decorator


# 3. Endpoint using Path, Query, and Body inside @bik_api Custom Decorator

@bik_api(
    api_name="/slack/channels/{channel_id}/events",  # {channel_id} is in URL -> Path Param
    methods=["POST"],
    auth_types=[AuthTypes.PUBLIC],
    router=router,
    tags=["Slack Integration"],
)
def handle_slack_channel_event(
    channel_id: str,                    # 1. PATH PARAMETER (matches {channel_id} in URL)
    payload: EventPayload,              # 2. REQUEST BODY (Pydantic model)
    notify_admin: bool = False,         # 3. QUERY PARAMETER (scalar, defaults to False -> ?notify_admin=true)
    priority: Optional[str] = "normal", # 4. QUERY PARAMETER (scalar, defaults to "normal" -> ?priority=high)
):
    """
    This endpoint processes a Slack event.
    FastAPI parses channel_id from path, payload from request body, and notify_admin/priority from query string.
    """
    return {
        "status": "success",
        "path_param_channel_id": channel_id,
        "body_payload": payload,
        "query_param_notify_admin": notify_admin,
        "query_param_priority": priority,
    }


# 4. Include router into the main FastAPI application
app.include_router(router)


# Main Root Route
@app.get("/")
def root():
    return {
        "message": "Welcome to Custom Route Decorator Demo!",
        "endpoint": "/slack/channels/C12345/events?notify_admin=true&priority=high",
    }


# To run this file:
# uvicorn 07_advanced_routing.03_custom_route_decorators:app --reload
