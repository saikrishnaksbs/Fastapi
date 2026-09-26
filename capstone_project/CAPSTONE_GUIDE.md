# Exhaustive Master Guide: FastAPI & Modern SQLAlchemy 2.0

Welcome to the exhaustive reference manual for **FastAPI** (Modules 01–12) and **Modern SQLAlchemy 2.0** (Modules 01–08). This document covers every single concept, syntax rule, relationship type, loading strategy, and architectural pattern implemented in [`main_app.py`](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/capstone_project/main_app.py).

---

## 📑 Complete Curriculum Concepts Index

---

### PART 1: Modern SQLAlchemy 2.0 Core & ORM (Modules 01–08)

#### 1. Engine & Connections (`01_engine_and_connections`)
* **Engine Creation**: `create_engine("sqlite:///...", echo=False, pool_size=5, max_overflow=10)`
* **Connection Contexts**:
  * `with engine.connect() as conn`: Low-level connection, explicit `conn.commit()` required.
  * `with engine.begin() as conn`: Automatic transaction context; commits on exit, rollbacks on exception.
* **Raw SQL & Parameter Binding**: `conn.execute(text("SELECT * FROM users WHERE name = :name"), {"name": "Alice"})`
* **Scalar Fetching**: `result.scalar()`, `result.all()`, `result.first()`

#### 2. Declarative Mapping 2.0 (`02_declarative_mapping`)
* **Subclassing `DeclarativeBase`**:
  ```python
  class Base(DeclarativeBase):
      pass
  ```
* **Mapped Column Attributes**: Using `Mapped[T]` and `mapped_column()`:
  * `id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)`
  * `username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)`
  * `role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole))`
  * `metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)`
  * `created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())`

#### 3. Session & Unit of Work (`03_session_and_crud`)
* **Lifecycle**: `sessionmaker(bind=engine, expire_on_commit=False)`
* **Unit of Work API**: `session.add()`, `session.add_all()`, `session.commit()`, `session.rollback()`, `session.flush()`, `session.refresh()`, `session.get()`, `session.delete()`.
* **Select Query Statements**:
  * `select(User).where(...).order_by(desc(...)).offset(0).limit(10)`
  * Operators: `and_()`, `or_()`, `not_()`, `in_()`, `like()`, `ilike()`, `is_()`
* **Scalar Results Execution**: `session.scalars(stmt).all()`, `scalar_one()`, `scalar_one_or_none()`, `first()`.

#### 4. Relationships & Loading Strategies (`04_relationships_and_joins`)
* **Standard 1:1**: `profile: Mapped[Optional[UserProfile]] = relationship("UserProfile", uselist=False, cascade="all, delete-orphan")`
* **Standard 1:N & N:1**: `posts: Mapped[List[Post]] = relationship("Post", back_populates="author")`
* **Standard M:N**: `tags: Mapped[List[Tag]] = relationship(Tag, secondary=capstone_post_tags)`
* **Association Object M:N**: `OrderItem` mapping `Order` and `Product` with extra attributes (`quantity`, `unit_price`).
* **Self-Referential 1:1**: `mentor: Mapped[Optional[PeerUser]] = relationship("PeerUser", remote_side=[id], uselist=False)`
* **Self-Referential 1:N**: `manager: Mapped[Optional[Employee]] = relationship("Employee", remote_side=[id], back_populates="subordinates")`
* **Self-Referential M:N**: Social followers network using self-referential association table with explicit `primaryjoin` & `secondaryjoin`.
* **Joins & Aliasing**: `select().join()`, `select().outerjoin()`, `aliased(Employee)`
* **Loading Strategies**:
  * `selectinload()`: 2 SQL queries (`WHERE id IN (...)`) for collections (1:N, M:N).
  * `joinedload()`: 1 SQL query (`LEFT OUTER JOIN`) for scalar objects (N:1, 1:1).
  * `subqueryload()`: Eager loading via subqueries for nested collections.
  * `contains_eager()`: Populates relationship attributes when manually specifying `.join()`.
  * `lazy="raise"`: Throws exception on unexpected lazy access (production N+1 guardrail).
  * `WriteOnlyMapped[T]`: High-performance queryable loading for massive collections where `.select()` is called directly on relationship.

#### 5. Advanced Relational Queries (`05_advanced_queries`)
* **Aggregations**: `func.count()`, `func.sum()`, `func.avg()`, `func.min()`, `func.max()`
* **Grouping & HAVING**: `select(Product.category, func.sum(Product.price)).group_by(Product.category).having(func.count() >= 1)`
* **Subqueries & CTEs**: `.subquery()`, `.scalar_subquery()`, `.cte("high_stock_cte")`
* **Window Functions**: `func.rank().over(partition_by=Product.category, order_by=Product.price.desc())`
* **Conditional Logic**: `case((Product.price >= 500, "Premium"), else_="Budget")`
* **Bulk DML**: `insert().returning()`, `update().where().returning()`, `delete().where().returning()`

#### 6. Async SQLAlchemy (`06_async_sqlalchemy`)
* `create_async_engine()`, `AsyncSession`, `async_sessionmaker`, `conn.run_sync()`.

#### 7. Transactions & Events (`07_transactions_and_events`)
* **Nested Transactions / Savepoints**: `with session.begin_nested():`
* **Event Listeners**: `@event.listens_for(User, "before_insert")` and `before_update` timestamp auditing.

#### 8. Database Migrations with Alembic (`08_alembic_migrations`)
* `alembic init`, `target_metadata = Base.metadata`, `alembic revision --autogenerate`, `alembic upgrade head`, `alembic downgrade -1`.

---

### PART 2: FastAPI Framework Core (Modules 01–12)

#### 1. Basics (`01_basics`)
* Path parameters (`/items/{id}`), Query parameters (defaults, optional, required, bool conversion), Request bodies (`BaseModel`), Mixed parameters.

#### 2. Request Validation (`02_request_validation`)
* Metadata & bounds via `Path(..., ge=1)`, `Query(..., pattern=...)`, `Field(..., gt=0)`, strict payload enforcement via `ConfigDict(extra="forbid")`.

#### 3. Response Handling (`03_response_handling`)
* `response_model`, `response_model_exclude_unset=True`, status codes `status.HTTP_201_CREATED`, `HTTPException`, `HTMLResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`.

#### 4. Dependency Injection (`04_dependencies`)
* `Depends()`, Sub-dependencies (dependencies depending on dependencies), `Cookie(None)`, `Header(None)`, Yield dependencies (`yield db`), Router-level global dependencies (`dependencies=[Depends(...)]`).

#### 5. Security & Authentication (`05_security_and_auth`)
* API Key schemes (`APIKeyHeader`, `APIKeyQuery`), OAuth2 Password Bearer (`OAuth2PasswordBearer`, `OAuth2PasswordRequestForm`), Passlib bcrypt password hashing, `pyjwt` JWT encoding/decoding with `exp`, `get_current_user`.

#### 6. Databases & ORM (`06_databases_and_orm`)
* Lifespan setup (`@asynccontextmanager`), `SessionLocal` yield dependency, full CRUD operations.

#### 7. Advanced Routing (`07_advanced_routing`)
* `APIRouter`, route prefixes, OpenAPI tags/summaries/descriptions, **Custom Route Decorator (`@custom_api_decorator`)** using `router.add_api_route()` and `functools.wraps`. Route matching order precedence (`/users/me` defined before `/users/{id}`).

#### 8. Middleware & CORS (`08_middleware_and_cors`)
* `CORSMiddleware` (origins, credentials, methods, headers), Custom HTTP Middleware (`@app.middleware("http")`) injecting `X-Process-Time`.

#### 9. Background Tasks & Lifespan (`09_background_tasks_and_events`)
* Post-response non-blocking operations via `BackgroundTasks.add_task(...)`, `@asynccontextmanager` app lifespan.

#### 10. WebSockets (`10_websockets`)
* Bi-directional endpoints (`@app.websocket`), connection handshake (`await websocket.accept()`), `ConnectionManager` pool, broadcasting, personal messaging (`send_personal_message`), `WebSocketDisconnect`.

#### 11. Automated Testing (`11_testing`)
* Synchronous testing with `TestClient(app)`, Asynchronous testing with `httpx.AsyncClient` and `ASGITransport`, Dependency overriding via `app.dependency_overrides` with cleanup (`app.dependency_overrides.clear()`).

#### 12. Deployment & Configuration (`12_deployment_and_config`)
* `pydantic-settings` (`BaseSettings`, `SettingsConfigDict`), `.env` file loading, `@lru_cache` settings dependency.

---

## 🚀 Execution Commands

Execute the master capstone application server:
```bash
python3 capstone_project/main_app.py
```

Run tests against all capstone features:
```bash
pytest capstone_project/main_app.py
```
