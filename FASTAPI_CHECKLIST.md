# Master FastAPI & Modern SQLAlchemy 2.0 Revision Checklist (Hierarchical Tree with Diagnostics)

> **Target Role**: Senior Backend Engineer / SDE-2 (FastAPI, Modern SQLAlchemy 2.0, Asynchronous Microservices)  
> **Source Directory**: [/Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/)  
> **Format**: 20 Master Topics with 2-Level Nested Active Recall Trees (`  - |__ **Category**` -> `      - |__ Details & Traps`).  
> **How to Revise**:
> 1. Open this file in **VS Code Markdown Preview** (`Cmd + K, V`) to view the interactive checkboxes and hierarchical tree branches.
> 2. Track your passes with the checkboxes (`- [ ]`) across endpoints, Pydantic schemas, dependency injection, and async ORM sessions.

---

## 📊 High-Level Curriculum Dashboard

- [ ] **PART I: FASTAPI CORE ARCHITECTURE** (Topics 1 to 12)
- [ ] **PART II: MODERN SQLALCHEMY 2.0 & ASYNC ORM** (Topics 13 to 20)

---

### [ ] Topic 1. FastAPI Basics & Request-Response Foundations

- [ ] **Box 1: Routing & ASGI Architecture**
  - |__ **ASGI Server Architecture**
      - |__ ASGI specification (Asynchronous Server Gateway Interface) vs WSGI
      - |__ Uvicorn server worker process model and event loop integration
      - |__ FastAPI app lifecycle initialization (`FastAPI()`, title, version, docs_url)
  - |__ **Path & Query Parameters**
      - |__ Path parameters syntax: `@app.get("/items/{item_id}")` with automatic type coercion
      - |__ Query parameters with default values, optional types (`int | None = None`)
      - |__ Parameter conversions: Booleans (1, true, yes parsed automatically), Enums as path params

- [ ] **Box 2: Request Body & Pydantic Data Binding**
  - |__ **Pydantic Model Payloads**
      - |__ Declaring JSON request bodies via Pydantic `BaseModel` subclasses
      - |__ Mixed parameters: Disambiguating Path, Query, and Request Body in endpoint signatures
      - |__ Multiple body parameters: `Body(embed=True)` forcing explicit top-level JSON keys

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **FastAPI Basics Gotchas**
      - |__ Trap 1: Defining `def` instead of `async def` on endpoints: Regular `def` runs in external threadpool, `async def` runs on event loop
      - |__ Trap 2: Order of route definitions: Static routes (`/users/me`) must be defined BEFORE parameter routes (`/users/{user_id}`)
      - |__ Trap 3: Query vs Body confusion: Primitive non-path arguments default to query parameters, Pydantic models default to body

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **FastAPI Parameter Resolver**
      - |__ How FastAPI inspects function signatures using `inspect.signature` and resolves parameters into OpenAPI schema components

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **FastAPI vs Flask vs Django**
      - |__ FastAPI: Native async, automatic OpenAPI 3.0 docs, Pydantic data validation, ultra-fast
      - |__ Flask: Minimalist, synchronous WSGI default, manual serialization
      - |__ Django: Monolithic batteries-included, synchronous ORM default, heavy footprint

---

### [ ] Topic 2. Request Validation & Pydantic V2 Deep Dive

- [ ] **Box 1: Parameter Constraint Validation**
  - |__ **Field, Path & Query Metadata**
      - |__ `Path(...)`, `Query(...)`, `Header(...)`, `Cookie(...)` constraint parameters
      - |__ Numeric validation: `ge`, `gt`, `le`, `lt`, `multiple_of`
      - |__ String validation: `min_length`, `max_length`, `pattern` (regex constraints)
  - |__ **Schema Configuration & Extras**
      - |__ Pydantic V2 `model_config = ConfigDict(extra='forbid')` rejecting unauthorized fields
      - |__ Custom field aliases: `Field(alias="user_name", validation_alias=...)`

- [ ] **Box 2: Custom Validators & Annotated Pattern**
  - |__ **Pydantic V2 Validators**
      - |__ `@field_validator('field_name', mode='before'|'after')` for field-level sanitization
      - |__ `@model_validator(mode='after')` for cross-field validation rules
      - |__ Modern Python typing: `Annotated[int, Path(ge=1)]` decoupling metadata from parameter defaults

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Validation Gotchas**
      - |__ Trap 1: Pydantic V1 vs V2 syntax changes (`@validator` vs `@field_validator`, `class Config` vs `model_config`)
      - |__ Trap 2: Modifying values in `@field_validator` without returning the modified value raises validation error

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Pydantic Core (pydantic-core in Rust)**
      - |__ Compilation of Python type hints into Rust validation trees yielding 5-20x throughput increases

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Input Validation Strategies**
      - |__ Schema-level validation (Pydantic model) vs Parameter-level validation (Query/Path) vs Route dependencies

---

### [ ] Topic 3. Response Handling, Serialization & Custom Exceptions

- [ ] **Box 1: Response Models & Filtering**
  - |__ **Response Schema Filtering**
      - |__ `response_model=UserOut` stripping sensitive fields (e.g. password_hash) from response
      - |__ Response model flags: `response_model_exclude_unset`, `response_model_exclude_none`
      - |__ Return type annotations (`-> UserOut`) automatically inferred as response_model in FastAPI 0.100+

- [ ] **Box 2: Status Codes, Exceptions & Responses**
  - |__ **HTTP Exceptions & Handlers**
      - |__ Raising `HTTPException(status_code=404, detail="Item not found", headers=...)`
      - |__ Custom exception classes with `@app.exception_handler(CustomException)`
      - |__ Custom response types: `JSONResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Response Gotchas**
      - |__ Trap 1: Returning ORM model instances without enabling `from_attributes=True` (formerly `orm_mode=True`) in Pydantic schema
      - |__ Trap 2: Leaking internal traceback details in production when catching generic 500 exceptions

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **FastAPI Response Serialization Pipeline**
      - |__ Serialization flow: Endpoint return value -> Pydantic `model_validate` -> `model_dump(mode='json')` -> Starlette JSONResponse

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **StreamingResponse vs FileResponse**
      - |__ StreamingResponse: Chunked transfer encoding for large dynamic iterators / LLM token streams
      - |__ FileResponse: Direct asynchronous file transfers using OS sendfile syscalls

---

### [ ] Topic 4. Dependency Injection System (DI)

- [ ] **Box 1: Hierarchical Dependency Injection**
  - |__ **Dependency Declarations**
      - |__ `Depends(get_db)`: Decoupling business logic, database sessions, and auth checks
      - |__ Sub-dependencies: Dependencies depending on other nested dependencies (dependency tree resolution)
      - |__ Dependency caching: `use_cache=True` (default) sharing dependency instance across single request

- [ ] **Box 2: Yield Dependencies & Lifecycles**
  - |__ **Yield Dependencies (Resource Teardown)**
      - |__ Generator dependencies using `yield` (e.g. `with Session() as session: yield session`)
      - |__ Post-request cleanup: Code after `yield` executes reliably even if endpoint raises exception
  - |__ **Global & Router Level Dependencies**
      - |__ Router dependencies: `APIRouter(dependencies=[Depends(verify_token)])`
      - |__ Global dependencies: `FastAPI(dependencies=[Depends(...)])` running for every route

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **DI Traps**
      - |__ Trap 1: Swallowing exceptions in yield dependencies with bare try-except prevents FastAPI error handling
      - |__ Trap 2: Setting `use_cache=False` unnecessarily creating multiple redundant database connections per request

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **FastAPI Dependency Graph Resolution (DAG)**
      - |__ Topological sort of dependency nodes executed sequentially or concurrently before route handler invocation

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **FastAPI DI vs Middleware**
      - |__ Dependencies: Endpoint-scoped, typed, accessible in OpenAPI docs, parameter-driven
      - |__ Middleware: Global HTTP stream interceptor, untyped, runs for every request/response before routing

---

### [ ] Topic 5. Authentication, Security & OAuth2 Protocols

- [ ] **Box 1: Security Schemes & Bearer Tokens**
  - |__ **Security Utilities**
      - |__ `OAuth2PasswordBearer(tokenUrl="token")`: Integrated OpenAPI Swagger UI authorization modal
      - |__ `OAuth2PasswordRequestForm`: Form-encoded payload validation (`username`, `password`, `scope`)
      - |__ API Key Auth: `APIKeyHeader`, `APIKeyQuery`, `APIKeyCookie` security schemes

- [ ] **Box 2: JWT Tokens & Cryptography**
  - |__ **Token Lifecycle Management**
      - |__ Password hashing: `passlib` with `bcrypt` or `argon2`
      - |__ JWT generation: `pyjwt` encoding claims (`sub`, `exp`, `iat`, `role`) with HMAC-SHA256 or RSA-256
      - |__ Token verification dependency: Decoding token, validating expiration, and fetching current user

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Security Traps**
      - |__ Trap 1: Storing JWT tokens in unencrypted local storage vulnerable to XSS (use HttpOnly SameSite cookies)
      - |__ Trap 2: Failing to verify token algorithm in PyJWT allowing `alg: none` signature bypass attacks

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **OAuth2 Token Flow Specification (RFC 6749)**
      - |__ Resource Owner Password Credentials Grant and JWT signature verification mechanics

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Stateful Session Cookies vs Stateless JWT**
      - |__ Session Cookies: Server-side state, immediate invalidation capability, horizontal scaling requires Redis
      - |__ JWT: Stateless, distributed verification, revocation requires blacklist or short TTLs

---

### [ ] Topic 6. Advanced Routing, Modularization & APIRouter

- [ ] **Box 1: APIRouter Architecture**
  - |__ **Modular API Architecture**
      - |__ Splitting endpoints by resource (`users_router = APIRouter(prefix="/users", tags=["Users"])`)
      - |__ Nested sub-routers: `app.include_router(api_v1_router)`
      - |__ Common responses and status codes configured at router level

- [ ] **Box 2: OpenAPI Customization & Custom Route Classes**
  - |__ **Custom APIRoute & Docs**
      - |__ Custom `APIRoute`: Overriding `get_route_handler` for global request logging or performance timing
      - |__ OpenAPI documentation customization: tags_metadata, operation_id customization, swagger UI parameters

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Routing Traps**
      - |__ Trap 1: Trailing slash redirects: `/items/` vs `/items` causing 307 temporary redirects and payload drops
      - |__ Trap 2: Duplicate operation_ids generated across different routers breaking client SDK generators

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Starlette Routing Table**
      - |__ Radix tree pattern matching and route dispatching mechanics in Starlette

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Monolithic App vs APIRouter Micro-modules**
      - |__ Scalability, circular import prevention, and clean domain-driven design separation

---

### [ ] Topic 7. Middleware, CORS & Starlette Internals

- [ ] **Box 1: CORS & Built-in Middlewares**
  - |__ **Cross-Origin Resource Sharing (CORS)**
      - |__ `CORSMiddleware`: `allow_origins`, `allow_credentials`, `allow_methods`, `allow_headers`
      - |__ Preflight OPTIONS request handling and browser security model
      - |__ `GZipMiddleware`: Automatic response payload compression for payloads > 500 bytes

- [ ] **Box 2: Custom BaseHTTPMiddleware**
  - |__ **Custom HTTP Middleware**
      - |__ `@app.middleware("http")` pattern wrapping `call_next(request)`
      - |__ Request ID tracing: Generating UUID `X-Request-ID` and injecting into request headers & logs
      - |__ Performance timing middleware measuring request latency

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Middleware Traps**
      - |__ Trap 1: Reading request body inside BaseHTTPMiddleware consumes stream, making it unavailable to endpoint
      - |__ Trap 2: CORS wildcard `allow_origins=["*"]` combined with `allow_credentials=True` rejected by browsers

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Pure ASGI Middleware Pattern**
      - |__ Why BaseHTTPMiddleware has known performance and contextvars bugs; writing raw ASGI `__call__(scope, receive, send)`

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Raw ASGI Middleware vs BaseHTTPMiddleware**
      - |__ Raw ASGI: Ultra-high performance, streaming compatible, zero memory copy overhead
      - |__ BaseHTTPMiddleware: Ergonomic request/response objects, buffering overhead

---

### [ ] Topic 8. Background Tasks, Lifespan Events & Async I/O

- [ ] **Box 1: BackgroundTasks & In-Process Queues**
  - |__ **BackgroundTasks Execution**
      - |__ `background_tasks.add_task(send_email, email, message)`
      - |__ Execution model: Runs AFTER response is sent, inside the same server worker process
      - |__ Contrast with distributed task queues (Celery, ARQ, Dramatiq) for heavy background jobs

- [ ] **Box 2: Modern Application Lifespan Events**
  - |__ **Lifespan Context Manager (PEP 680)**
      - |__ Modern `@asynccontextmanager async def lifespan(app: FastAPI):`
      - |__ Startup phase: Initializing DB connection pools, HTTP clients, ML model loading
      - |__ Shutdown phase: Disconnecting pools, flushing buffers, graceful shutdown

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Background Task Traps**
      - |__ Trap 1: Using BackgroundTasks for long-running CPU or critical tasks: Worker restart loses all pending tasks
      - |__ Trap 2: Using legacy `@app.on_event("startup")` and `"shutdown"` (deprecated in modern FastAPI)

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Starlette Lifespan State Machine**
      - |__ ASGI `lifespan.startup` and `lifespan.shutdown` protocol messages sent by Uvicorn

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **BackgroundTasks vs Celery vs Redis Queue**
      - |__ BackgroundTasks: Lightweight, in-process, zero external dependencies, no retries/persistence
      - |__ Celery: Distributed broker, worker fleet, retry policies, task persistence, scheduling

---

### [ ] Topic 9. WebSockets & Real-Time Communication

- [ ] **Box 1: WebSocket Protocol & Endpoints**
  - |__ **WebSocket Lifecycle**
      - |__ `@app.websocket("/ws/{client_id}")`: Endpoint receiving `WebSocket` object
      - |__ Lifecycle methods: `await websocket.accept()`, `await websocket.receive_text()`, `await websocket.send_text()`, `await websocket.close()`
      - |__ Exception handling: `WebSocketDisconnect` handling for connection teardown

- [ ] **Box 2: Connection Manager & Broadcasting**
  - |__ **Multi-Client Broadcast Pattern**
      - |__ Building in-memory `ConnectionManager` tracking active WebSocket instances
      - |__ Broadcast loop sending messages concurrently across connected clients
      - |__ Scaling beyond single process: Redis Pub/Sub integration for multi-worker WebSocket synchronization

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **WebSocket Traps**
      - |__ Trap 1: Failing to catch WebSocketDisconnect causing uncaught server exceptions and leaked connection handles
      - |__ Trap 2: WebSocket auth cannot pass standard HTTP Authorization headers in browser JavaScript WebSocket API

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **WebSocket Handshake & Frame Encoding**
      - |__ HTTP 101 Switching Protocols upgrade handshake and RFC 6455 frame masking

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **WebSockets vs Server-Sent Events (SSE) vs Long Polling**
      - |__ WebSockets: Full-duplex bidirectional communication, low latency
      - |__ SSE: Half-duplex (server-to-client only), HTTP native, built-in reconnection, ideal for LLM token streaming

---

### [ ] Topic 10. Automated Testing & Async TestClient

- [ ] **Box 1: Synchronous & Asynchronous Testing**
  - |__ **Starlette TestClient vs HTTPX AsyncClient**
      - |__ `TestClient(app)`: Built on HTTPX, runs requests synchronously through the ASGI stack
      - |__ `httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test")` for native async testing
      - |__ Testing pytest fixtures: Creating temporary databases and isolated transaction rollbacks

- [ ] **Box 2: Dependency Overrides**
  - |__ **Test Dependency Overrides**
      - |__ `app.dependency_overrides[get_db] = override_get_db` replacing production DB with mock/SQLite
      - |__ Fixture teardown: `app.dependency_overrides.clear()` preventing cross-test pollution
      - |__ Mocking authentication dependencies for testing protected routes without real tokens

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Testing Traps**
      - |__ Trap 1: Forgetting to clear `app.dependency_overrides` between test runs leaking test doubles
      - |__ Trap 2: Using TestClient with async yield dependencies running into event loop thread mismatch

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **ASGITransport Mock Transport**
      - |__ In-memory pipe passing ASGI scope directly without opening real network TCP sockets

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **SQLite in-memory vs Dockerized PostgreSQL test containers**
      - |__ SQLite: Instant startup, dialect differences (JSON, arrays, enums missing)
      - |__ Testcontainers PostgreSQL: True production fidelity, slower CI run time

---

### [ ] Topic 11. Configuration, Pydantic-Settings & Production Deployment

- [ ] **Box 1: 12-Factor App Configuration (pydantic-settings)**
  - |__ **Settings Management**
      - |__ `BaseSettings` class with typed environment variables and automatic `.env` file loading
      - |__ `SettingsConfigDict(env_file='.env', extra='ignore')`
      - |__ Singleton settings dependency: `@lru_cache def get_settings() -> Settings:`

- [ ] **Box 2: Production ASGI Deployment**
  - |__ **Gunicorn + Uvicorn Worker Model**
      - |__ Running production servers: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
      - |__ Worker count formula: `(2 * CPU cores) + 1`
      - |__ Reverse proxy architecture: NGINX / Caddy handling SSL termination, rate limiting, and static files
      - |__ Docker containerization: Multi-stage Docker builds, non-root user execution, health checks

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Deployment Traps**
      - |__ Trap 1: Binding server to `127.0.0.1` inside Docker container prevents external traffic reaching container (must bind to `0.0.0.0`)
      - |__ Trap 2: Storing secrets in Docker image layers instead of injecting via runtime environment variables

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Unix Domain Sockets & Master-Worker Process Tree**
      - |__ Gunicorn master process signal handling (SIGHUP, SIGTERM) and zero-downtime worker reloads

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Uvicorn standalone vs Gunicorn Uvicorn workers**
      - |__ Uvicorn standalone: Single process or basic reload, ideal for development
      - |__ Gunicorn + Uvicorn: Multi-process process management, heartbeat monitoring, auto-restart

---

### [ ] Topic 12. Modern SQLAlchemy 2.0 Engine & Connection Pooling

- [ ] **Box 1: Engine Creation & Connection Lifecycles**
  - |__ **Core Engine Mechanics**
      - |__ `create_engine("postgresql+psycopg://...", echo=False, pool_size=5, max_overflow=10)`
      - |__ `engine.connect()` vs `engine.begin()` (automatic transaction commit on context exit)
      - |__ Executing raw SQL safely: `session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})`

- [ ] **Box 2: Connection Pool Management**
  - |__ **Pool Architectures**
      - |__ `QueuePool` (default for network databases), `NullPool` (for serverless / AWS Lambda), `StaticPool` (SQLite in-memory)
      - |__ Pool health checks: `pool_pre_ping=True` eliminating stale disconnected socket errors
      - |__ Pool exhaustion prevention: `pool_timeout` and monitoring checked-out connections

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Engine Traps**
      - |__ Trap 1: Sharing connection engine across forked processes causing shared socket corruption
      - |__ Trap 2: Omitting `pool_pre_ping=True` in cloud DB setups leading to OperationalError after database idle timeouts

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **QueuePool C-Level Socket Pool**
      - |__ Thread-safe queue dispensing DBAPI connections with checkin/checkout hooks

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **QueuePool vs NullPool**
      - |__ QueuePool: High-throughput persistent servers, reuses TCP handshakes
      - |__ NullPool: Ephemeral environments (FaaS, Celery batch forks), prevents connection limits

---

### [ ] Topic 13. SQLAlchemy 2.0 Declarative Mapping & Type Annotations

- [ ] **Box 1: DeclarativeBase & Mapped Columns**
  - |__ **Modern 2.0 Syntax**
      - |__ Base class: `class Base(DeclarativeBase): pass`
      - |__ Type-safe column declarations: `id: Mapped[int] = mapped_column(primary_key=True)`
      - |__ Nullable typing: `bio: Mapped[str | None] = mapped_column(String(255), nullable=True)`
      - |__ String length & indexed columns: `mapped_column(String(50), index=True, unique=True)`

- [ ] **Box 2: Advanced Field Types & Enums**
  - |__ **Specialized Column Types**
      - |__ Enum mapping: `status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus))`
      - |__ JSON / JSONB columns: `metadata_: Mapped[dict] = mapped_column(JSON)`
      - |__ Automatic timestamps: `created_at: Mapped[datetime] = mapped_column(server_default=func.now())`

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Mapping Traps**
      - |__ Trap 1: Mixing legacy 1.4 syntax (`Column(Integer, ...)` without `Mapped[T]`) losing IDE autocomplete and static type safety
      - |__ Trap 2: Mutable JSON column updates not detected by session without `MutableDict.as_mutable`

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **SQLAlchemy Mapper & Table Metadata**
      - |__ How `DeclarativeBase` constructs `Table` and `Mapper` objects during class definition time

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **SQLAlchemy 1.4 vs 2.0 Mapping**
      - |__ 1.4: Dynamic, loosely typed, `Column(...)` based
      - |__ 2.0: PEP 484 type-compliant, `Mapped[T]` and `mapped_column()`, fully mypy-compliant

---

### [ ] Topic 14. SQLAlchemy Session Lifecycle & Unit of Work

- [ ] **Box 1: Session & Unit of Work Pattern**
  - |__ **Session Management**
      - |__ `sessionmaker(bind=engine, expire_on_commit=False)`
      - |__ Session lifecycle states: Transient, Pending, Persistent, Detached
      - |__ Unit of Work: Changes tracked in memory; single flush writes batch SQL to DB in topological dependency order

- [ ] **Box 2: CRUD & Modern select() Queries**
  - |__ **Modern Query Construction**
      - |__ Constructing queries: `stmt = select(User).where(User.is_active == True).order_by(User.created_at.desc())`
      - |__ Execution & Fetching: `session.scalars(stmt).all()`, `session.scalar(stmt)`, `session.scalars(stmt).first()`
      - |__ Pagination: `.offset(skip).limit(limit)`
      - |__ In-place updates & deletes: `session.delete(instance)` and bulk execution `update(User).where(...).values(...)`

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Session Traps**
      - |__ Trap 1: `expire_on_commit=True` causing lazy load crashes after session closes when accessing attributes
      - |__ Trap 2: Calling `session.execute(select(User)).all()` returning Row tuples instead of model instances (use `session.scalars()`)

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Identity Map Pattern**
      - |__ Ensures that a single database row maps to exactly one unique Python object instance per session

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **session.flush() vs session.commit()**
      - |__ flush(): Sends SQL to database, assigns generated IDs, transaction stays open
      - |__ commit(): Flushes SQL, commits transaction permanently to disk, ends transaction

---

### [ ] Topic 15. Relationships, Cascades & The N+1 Query Problem

- [ ] **Box 1: Declaring Relationships**
  - |__ **Relationship Topologies**
      - |__ One-to-Many / Many-to-One: `relationship("Child", back_populates="parent")` and `ForeignKey("parent.id")`
      - |__ Many-to-Many: Associative association table with composite primary key foreign keys
      - |__ Cascade options: `cascade="all, delete-orphan"` ensuring children are deleted when unlinked from parent

- [ ] **Box 2: Solving the N+1 Query Problem**
  - |__ **Loading Strategies**
      - |__ The N+1 trap: Accessing related collection inside loop triggers N distinct SELECT queries
      - |__ `joinedload()`: Generates single SQL query with LEFT OUTER JOIN (ideal for 1:1 and Many-to-One)
      - |__ `selectinload()`: Executes second query using `WHERE id IN (...)` (ideal for 1:Many and Many:Many collections)
      - |__ `contains_eager()`: Populates relationship from manual explicit join query

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Relationship Traps**
      - |__ Trap 1: Using `joinedload()` on collections with pagination limit/offset produces incorrect row counts!
      - |__ Trap 2: Forgetting `back_populates` causing relationship synchronization issues in memory

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Lazy Loading Event Mechanics**
      - |__ Instrumenting attribute descriptors with event listeners that trigger SQL queries upon first access

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **joinedload() vs selectinload() vs subqueryload()**
      - |__ joinedload(): Best for single-parent references; duplicates parent data on collections
      - |__ selectinload(): Best for collections, clean 2-step query, safe with pagination
      - |__ subqueryload(): Legacy subquery approach, superseded by selectinload in 2.0

---

### [ ] Topic 16. Advanced SQL, Aggregations, CTEs & Window Functions

- [ ] **Box 1: Aggregations & Grouping**
  - |__ **SQL Functions & Grouping**
      - |__ Aggregate functions: `func.count()`, `func.sum()`, `func.avg()`, `func.max()`, `func.min()`
      - |__ Group by & Having: `select(User.role, func.count(User.id)).group_by(User.role).having(func.count(User.id) > 5)`
      - |__ Filtering aggregates: `func.count().filter(User.is_active == True)`

- [ ] **Box 2: Common Table Expressions (CTEs) & Window Functions**
  - |__ **Complex Querying**
      - |__ CTE definition: `cte = select(Order).where(...).cte("filtered_orders")`
      - |__ Window functions: `func.row_number().over(partition_by=User.dept_id, order_by=User.salary.desc())`
      - |__ Subqueries: `subq = select(func.avg(salary)).scalar_subquery()`

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Advanced SQL Traps**
      - |__ Trap 1: Group by queries without including all non-aggregated select columns causing SQL syntax errors
      - |__ Trap 2: Performing arithmetic on nullable columns without `func.coalesce(Column, 0)` yielding NULL results

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **SQLAlchemy Expression Language AST Compiler**
      - |__ Translating Python ClauseElements into dialect-specific SQL string queries

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **CTE vs Subquery**
      - |__ CTE: Reusable within same query, readable, supports recursive queries
      - |__ Subquery: Inline, evaluated per-row or as scalar value

---

### [ ] Topic 17. Asynchronous SQLAlchemy 2.0 (AsyncEngine & AsyncSession)

- [ ] **Box 1: Async Engine & Session Setup**
  - |__ **Async Architecture**
      - |__ Async DBAPI drivers: `asyncpg` for PostgreSQL, `aiosqlite` for SQLite
      - |__ Async engine: `create_async_engine("postgresql+asyncpg://...")`
      - |__ Async sessionmaker: `async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)`

- [ ] **Box 2: Async CRUD & Lazy Loading Restrictions**
  - |__ **Async Execution**
      - |__ Execution: `result = await session.execute(stmt)` and `items = result.scalars().all()`
      - |__ Lazy loading prohibition: Implicit lazy loading raises `MissingGreenlet` error in async!
      - |__ Explicit eager loading mandate: Must use `selectinload` or `joinedload` on every relationship

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Async SQLAlchemy Traps**
      - |__ Trap 1: MissingGreenlet error: Triggered when attempting to access an un-loaded relationship outside an eager load in async mode
      - |__ Trap 2: Using synchronous drivers (`psycopg2`) with `create_async_engine` crashing at startup

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Greenlet Async Adapter Pattern**
      - |__ How SQLAlchemy uses greenlet micro-threads to run synchronous-like ORM state machinery over async event loops

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Sync vs Async SQLAlchemy**
      - |__ Sync (psycopg2): Simple, reliable, threadpool overhead in FastAPI
      - |__ Async (asyncpg): Highest I/O concurrency, zero thread overhead, requires strict eager loading

---

### [ ] Topic 18. Transactions, Savepoints & Event Hooks

- [ ] **Box 1: Transaction Control & Savepoints**
  - |__ **Transaction Management**
      - |__ Explicit transactions: `async with session.begin(): ...` (commits on success, rolls back on exception)
      - |__ Nested transactions / Savepoints: `async with session.begin_nested(): ...`
      - |__ Partial rollbacks: Rolling back inner savepoint without aborting outer transaction

- [ ] **Box 2: Event Listeners & Audit Hooks**
  - |__ **SQLAlchemy Events**
      - |__ `@event.listens_for(Session, "before_commit")` for audit log injection
      - |__ Attribute events: `@event.listens_for(User.password, "set")` for automatic hashing
      - |__ Mapper events: `before_insert`, `after_update` hooks

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Transaction Traps**
      - |__ Trap 1: Calling `session.commit()` inside an active `begin()` context manager raises InvalidRequestError
      - |__ Trap 2: Mutating objects inside `after_commit` hooks: Transaction is already closed; mutations are lost

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Two-Phase Commit & ACID Guarantees**
      - |__ Isolation levels (Read Committed vs Repeatable Read vs Serializable) configured via `isolation_level` parameter

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Root Transaction vs Savepoint**
      - |__ Root Transaction: `BEGIN ... COMMIT/ROLLBACK` (atomic boundary for request)
      - |__ Savepoint: `SAVEPOINT sp ... ROLLBACK TO sp` (fine-grained error recovery)

---

### [ ] Topic 19. Database Migrations with Alembic

- [ ] **Box 1: Alembic Setup & Environment**
  - |__ **Alembic Initialization**
      - |__ `alembic init -t async migrations`: Async template configuration
      - |__ `env.py`: Configuring `target_metadata = Base.metadata` for autogeneration
      - |__ `alembic.ini`: Database URL configuration and logging setup

- [ ] **Box 2: Migration Revisions & Deployment**
  - |__ **Revision Workflow**
      - |__ Autogenerate migration: `alembic revision --autogenerate -m "add user table"`
      - |__ Applying migrations: `alembic upgrade head`
      - |__ Downgrading migrations: `alembic downgrade -1`
      - |__ Current status: `alembic current` and `alembic history`

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Alembic Traps**
      - |__ Trap 1: Alembic autogenerate cannot detect column renames (detects as DROP column + ADD column with data loss!)
      - |__ Trap 2: Autogenerate cannot detect custom enum mutations without explicit `compare_type=True` in `context.configure`

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Schema Diffing Engine**
      - |__ How Alembic compares Python `MetaData` models with live database `Information_Schema` tables

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Alembic vs Django Migrations**
      - |__ Alembic: Explicit Python code revisions, requires manual import in env.py, fine-grained control
      - |__ Django: Fully automated, auto-detects renames, tightly coupled to Django ORM

---

### [ ] Topic 20. End-to-End Enterprise Architecture & Performance Tuning

- [ ] **Box 1: Clean Architecture & Repository Pattern**
  - |__ **Layered Architecture**
      - |__ Presentation Layer (FastAPI Routers, Pydantic schemas)
      - |__ Business Layer (Services, domain models, validations)
      - |__ Data Access Layer (Repositories, SQLAlchemy models, queries)
      - |__ Database Dependency: Providing session to repository via FastAPI `Depends()`

- [ ] **Box 2: Database & API Performance Optimization**
  - |__ **Optimization Checkpoints**
      - |__ Database Indexes: B-Tree vs Hash vs GIN (for JSONB / full-text search)
      - |__ Connection Pooling: Sizing pool appropriately for worker processes
      - |__ Query analysis: Inspecting generated SQL via `echo=True` or `EXPLAIN ANALYZE`
      - |__ Redis Caching: Caching read-heavy endpoint outputs with cache invalidation on write

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Production Traps**
      - |__ Trap 1: Multiplying connection pool by worker processes exhausting PostgreSQL `max_connections` (e.g. 10 workers * 20 connections = 200 conns)
      - |__ Trap 2: Missing database indexes on foreign keys causing slow sequential table scans during JOIN operations

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **PostgreSQL EXPLAIN ANALYZE Cost Model**
      - |__ Sequential Scan vs Index Scan vs Index Only Scan vs Bitmap Heap Scan

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **ORM vs Raw SQL (Asyncpg/psycopg)**
      - |__ ORM: Type safety, migration support, maintainability, minor translation overhead
      - |__ Raw SQL: Maximum possible throughput, manual mapping, zero abstractions
