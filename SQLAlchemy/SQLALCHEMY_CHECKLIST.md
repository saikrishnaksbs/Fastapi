# Master Modern SQLAlchemy 2.0 SDE-2/Senior Revision Checklist

> **Target Role**: Senior Backend Engineer / Database Architect / SDE-2 & SDE-3 (Modern SQLAlchemy 2.0, Async ORM, High-Concurrency Storage)  
> **Source Directory**: [/Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/SQLAlchemy/](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/SQLAlchemy/)  
> **Format**: 10 Master Topic Modules with Hierarchical Active Recall Trees (`  - |__ **Category**` -> `      - |__ Details, Traps & Architecture Invariants`).  
> **How to Revise**:
> 1. Open this file in **VS Code Markdown Preview** (`Cmd + K, V`) to view the interactive checkboxes and hierarchical tree branches.
> 2. Use the checkboxes (`- [ ]`) to track your 1st Pass (Syntax & Concepts), 2nd Pass (Internals & Active Recall), and 3rd Pass (System Design & Code Interview Drill).

---

## 📊 High-Level Curriculum Dashboard

- [ ] **PART I: CORE ARCHITECTURE, ENGINE & DECLARATIVE MAPPING** (Topics 1 to 3)
- [ ] **PART II: QUERYING, ADVANCED RELATIONSHIPS & LOADING STRATEGIES** (Topics 4 to 7)
- [ ] **PART III: ADVANCED SQL, ASYNC ORM, TRANSACTIONS & MIGRATIONS** (Topics 8 to 10)

---

### [ ] Topic 1. Engine Architecture, Connection Pooling & Raw SQL Execution

- [ ] **Box 1: Engine Creation & Connection Lifecycles**
  - |__ **Engine Fundamentals**
      - |__ `create_engine(url, echo=False, pool_size=5, max_overflow=10)`
      - |__ Connection acquisition: `engine.connect()` (manual transaction management)
      - |__ Context transaction: `with engine.begin() as conn:` (automatic COMMIT on exit, ROLLBACK on exception)
      - |__ Dialect translation: Converting Python SQL AST into target RDBMS SQL dialect (PostgreSQL, MySQL, SQLite)

- [ ] **Box 2: Connection Pool Management**
  - |__ **Pool Implementations**
      - |__ `QueuePool`: Standard thread-safe FIFO connection pool for persistent server processes
      - |__ `NullPool`: Zero-connection caching (creates/closes socket per request; mandatory for AWS Lambda / FaaS)
      - |__ `StaticPool`: Single persistent connection pool for in-memory SQLite (`:memory:`)
      - |__ Pool health checks: `pool_pre_ping=True` emitting `SELECT 1` to prune stale/disconnected TCP sockets
      - |__ Sizing parameters: `pool_size` (baseline), `max_overflow` (surge ceiling), `pool_timeout` (wait seconds)

- [ ] **Box 3: Parameterized Raw SQL Execution**
  - |__ **text() Construct & Binding**
      - |__ `text("SELECT * FROM users WHERE status = :status")`: Prepared statement construct
      - |__ Parameter binding: `conn.execute(stmt, {"status": "active"})` preventing SQL injection
      - |__ Result inspection: `result.mappings().all()` returning list of dictionary-like `RowMapping` objects

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Engine Traps**
      - |__ Trap 1: Forking a process (e.g. Celery / Gunicorn preload) sharing an Engine inherits open socket descriptors causing connection collision! Must call `engine.dispose(close=False)` in worker init
      - |__ Trap 2: Omitting `pool_pre_ping=True` in cloud setups: Firewall idle timeouts drop TCP sockets silently, causing `OperationalError: server closed the connection unexpectedly`
      - |__ Trap 3: String formatting SQL (`f"SELECT * WHERE id = '{id}'"`) instead of `text()` parameters introducing critical SQL injection vulnerabilities

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **QueuePool Mutex & Semaphore Architecture**
      - |__ Thread-safe checkout queue; acquiring connection decrements semaphore, waiting up to `pool_timeout` before raising `TimeoutError`

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **QueuePool vs NullPool**
      - |__ QueuePool: High-throughput microservices, reuses TCP handshakes, memory persistent
      - |__ NullPool: Ephemeral environments (Serverless, FaaS, short-lived CLI batch scripts), prevents connection saturation

---

### [ ] Topic 2. Declarative Mapping 2.0, Mapped[T] & Modern Schema Types

- [ ] **Box 1: Modern DeclarativeBase & Mapped Annotations**
  - |__ **Unified 2.0 Class Definition**
      - |__ Base declaration: `class Base(DeclarativeBase): pass` (replaces legacy `declarative_base()`)
      - |__ Primary keys: `id: Mapped[int] = mapped_column(primary_key=True)`
      - |__ Nullability inference: `Mapped[str]` infers `nullable=False`; `Mapped[str | None]` infers `nullable=True`
      - |__ Column constraints: `mapped_column(String(50), unique=True, index=True, server_default="active")`

- [ ] **Box 2: Advanced Column Types & Enums**
  - |__ **Data Types**
      - |__ Python Enum integration: `status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus))`
      - |__ JSON / JSONB support: `metadata_: Mapped[dict] = mapped_column(JSON)` (Postgres `JSONB` for indexing)
      - |__ DateTime with timezone: `created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())`
      - |__ Automatic `__repr__`: Writing custom or automated `__repr__` for clean debugging without lazy-load side effects

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Mapping Traps**
      - |__ Trap 1: Using legacy 1.4 syntax (`name = Column(String)`) losing static type-checking and Mypy auto-complete
      - |__ Trap 2: In-place mutation of standard JSON columns (`user.metadata_['key'] = 'val'`): SQLAlchemy does not track in-place mutations without `MutableDict.as_mutable(JSON)`!

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Declarative Meta Registration**
      - |__ How `DeclarativeBase` metaclass translates type annotations into `Table` metadata and `ColumnProperty` descriptors at module load time

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Core Table vs ORM DeclarativeBase**
      - |__ Core Table (`Table('users', metadata, ...)`): Explicit relational schema representation
      - |__ DeclarativeBase: Combines relational schema definition with Python domain object classes

---

### [ ] Topic 3. Session Lifecycle, Unit of Work & Identity Map Internals

- [ ] **Box 1: Session Architecture & sessionmaker**
  - |__ **Session Mechanics**
      - |__ `sessionmaker(bind=engine, expire_on_commit=False)`
      - |__ Session as workspace: Represents in-memory transaction and object state buffer
      - |__ Session states: Transient (new, unattached), Pending (`session.add`), Persistent (attached, in DB), Detached (session closed)

- [ ] **Box 2: Unit of Work & Identity Map**
  - |__ **Object Management**
      - |__ Unit of Work: Changes batched in memory; `flush()` sends topological insert/update/delete SQL to database
      - |__ Identity Map: Guarantees that within a session, `session.get(User, 1) is session.get(User, 1)` (exact same Python heap object!)
      - |__ Lifecycle operations: `session.add()`, `session.commit()`, `session.rollback()`, `session.flush()`, `session.refresh(obj)`, `session.expunge(obj)`

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Session Traps**
      - |__ Trap 1: `expire_on_commit=True` default: Accessing attributes on returned objects after session closes raises `DetachedInstanceError`! Always set `expire_on_commit=False` in web apps
      - |__ Trap 2: Keeping sessions open across threads: `Session` is strictly NOT thread-safe; never share session instances across threads

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Identity Map Hash Cache & Topological Sorter**
      - |__ Resolves foreign key dependencies between pending objects before flushing SQL to avoid constraint violations

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **session.flush() vs session.commit()**
      - |__ flush(): Sends pending SQL statements to DB, triggers DB constraints and generates primary keys; transaction stays open
      - |__ commit(): Calls flush(), commits the database transaction permanently to disk, releases locks

---

### [ ] Topic 4. Select Queries, Modern Filtering, Pagination & Execution Modes

- [ ] **Box 1: Modern select() Syntax**
  - |__ **2.0 Query Construction**
      - |__ `stmt = select(User).where(User.is_active == True).order_by(User.created_at.desc())`
      - |__ Multiple criteria: `where(User.age >= 18, User.country == 'US')` (implicit AND)
      - |__ Logical operators: `and_()`, `or_()`, `not_()` for complex boolean trees
      - |__ Pattern lookups: `User.name.like('A%')`, `User.name.ilike('a%')` (case-insensitive), `User.id.in_([1, 2, 3])`

- [ ] **Box 2: Execution Results & Pagination**
  - |__ **Fetching & Pagination**
      - |__ Scalar execution: `session.scalars(stmt).all()` returning list of Model instances
      - |__ Single row fetching: `session.scalars(stmt).first()`, `session.scalars(stmt).one()`, `session.scalars(stmt).one_or_none()`
      - |__ Offset-limit pagination: `stmt.offset(skip).limit(limit)`
      - |__ Keyset (Cursor) pagination: `where(User.id > last_seen_id).order_by(User.id).limit(page_size)` for O(1) performance

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Query Traps**
      - |__ Trap 1: Using `session.execute(select(User)).all()` returns list of `Row` tuples `[(User,), (User,)]`; must call `session.scalars(stmt).all()` to get pure User instances
      - |__ Trap 2: Calling `.one()` on a query returning multiple rows raises `MultipleResultsFound`; returning zero rows raises `NoResultFound` (use `one_or_none()`)

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **ClauseElement Compilation**
      - |__ Python operator overloading (`==`, `!=`, `<`, `>`) compiling expressions into SQL binary operation nodes

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Legacy session.query() vs Modern select()**
      - |__ session.query(): 1.x legacy, tied to ORM session, inflexible
      - |__ select(): Unified 2.0 style, identical syntax across Core and ORM, supports subqueries & CTEs seamlessly

---

### [ ] Topic 5. Relational Modeling: 1:1, 1:N, N:1 & M:N Association Patterns

- [ ] **Box 1: One-to-Many & One-to-One Relationships**
  - |__ **Standard Associations**
      - |__ One-to-Many: `user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))`
      - |__ Parent declaration: `posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")`
      - |__ Child declaration: `author: Mapped["User"] = relationship(back_populates="posts")`
      - |__ One-to-One: Child defines `user_id` as unique ForeignKey; parent declares `profile: Mapped["Profile"] = relationship(uselist=False)`

- [ ] **Box 2: Many-to-Many (Association Table vs Association Object Pattern)**
  - |__ **M:N Topologies**
      - |__ Simple M:N: `Table("post_tags", Base.metadata, Column("post_id", ForeignKey(...)), Column("tag_id", ForeignKey(...)))`
      - |__ Simple relationship: `tags: Mapped[list["Tag"]] = relationship(secondary="post_tags", back_populates="posts")`
      - |__ Association Object Pattern: Full intermediate model `class Enrollment(Base):` storing extra payload columns (e.g. `enrolled_date`, `grade`)

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Relationship Traps**
      - |__ Trap 1: Forgetting `cascade="all, delete-orphan"` on 1:N relations leaves orphaned child rows referencing non-existent parent IDs
      - |__ Trap 2: Using strings in `relationship()` without quotes when target class is defined lower in the file causing NameError

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **RelationshipProperty & Backref Instrumentation**
      - |__ How bidirectional event listeners keep `user.posts` and `post.author` in sync in Python memory before flush

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Association Table vs Association Object Pattern**
      - |__ Association Table (`secondary`): Best when link contains ONLY the two foreign keys
      - |__ Association Object Pattern: Mandatory whenever the link contains extra metadata (e.g. timestamps, roles, status)

---

### [ ] Topic 6. Self-Referential Hierarchies & Graph Topologies

- [ ] **Box 1: Hierarchical Trees & Organizations**
  - |__ **Self-Referential 1:N (Org Manager Hierarchy)**
      - |__ Model definition: `class Employee(Base):`
      - |__ Foreign key: `manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"))`
      - |__ Relationships:
          - `manager: Mapped["Employee | None"] = relationship(back_populates="direct_reports", remote_side="Employee.id")`
          - `direct_reports: Mapped[list["Employee"]] = relationship(back_populates="manager")`

- [ ] **Box 2: Self-Referential Graphs & Mentors**
  - |__ **Self-Referential 1:1 & M:N (Followers Graph)**
      - |__ Self-Referential 1:1: `mentor_id` with `uselist=False` (Peer Mentors)
      - |__ Self-Referential M:N (Social Network Followers):
          - Association table with `follower_id` and `followed_id` both referencing `users.id`
          - `following: Mapped[list["User"]] = relationship(secondary=follows, primaryjoin=..., secondaryjoin=...)`
      - |__ Querying graphs: Using `aliased()` to join employee table against itself

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Self-Referential Traps**
      - |__ Trap 1: Omitting `remote_side` on self-referential relationships: SQLAlchemy cannot determine which side is the parent/child and crashes!
      - |__ Trap 2: Forgetting `aliased()` when joining a self-referential model causing ambiguous column SQL compilation errors

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Aliased Class SQL Generation**
      - |__ How `aliased(Employee)` assigns separate SQL table aliases (`employees_1`, `employees_2`) in generated queries

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Adjacency List vs Nested Sets vs Path Enumeration**
      - |__ Adjacency List (SQLAlchemy native self-FK): Simplest updates, requires recursive CTEs for deep tree lookups
      - |__ Path Enumeration (Materialized Path `/1/4/12/`): Ultra-fast subtree lookups, slower re-parenting

---

### [ ] Topic 7. Relationship Loading Strategies & The N+1 Solution Matrix

- [ ] **Box 1: The N+1 Query Problem & Lazy Loading**
  - |__ **Loading Behaviors**
      - |__ `lazy="select"` (Default): Emits a new `SELECT` query the first time relationship attribute is accessed
      - |__ The N+1 Problem: Looping over 100 users and accessing `user.posts` triggers 1 initial query + 100 secondary queries!
      - |__ `lazy="raise"` / `lazy="raise_on_sql"`: Proactively raises an exception if relationship would trigger lazy SQL (best practice for tests/async)

- [ ] **Box 2: Eager Loading Strategies**
  - |__ **Eager Loaders**
      - |__ `selectinload(User.posts)`: Emits 2nd query using `WHERE user_id IN (1, 2, ...)` (optimal for 1:N and M:N collections)
      - |__ `joinedload(Post.author)`: Emits 1 query with `LEFT OUTER JOIN` (optimal for 1:1 and N:1 single-parent references)
      - |__ `contains_eager(User.posts)`: Populates relationship from manual explicit `join(User.posts)` query
      - |__ `WriteOnlyMapped[T]`: For huge collections (100k+ rows) returning lazy query rather than loading list into memory

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Loading Traps**
      - |__ Trap 1: Using `joinedload()` on collections with pagination (`limit(10)`): Produces incorrect row counts due to duplicated parent rows! Must use `selectinload()`
      - |__ Trap 2: Filtering on a joinedload: `joinedload()` does NOT filter the parent rows; it only instructs how to load the relationship!

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **selectinload In-Memory Key Binding**
      - |__ Executes second batch query and binds child instances directly into parent object instance collections in memory

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **joinedload vs selectinload vs subqueryload**
      - |__ joinedload: 1 query (JOIN), best for Many-to-One / One-to-One, broken with collection pagination
      - |__ selectinload: 2 queries (IN clause), best for One-to-Many / Many-to-Many, safe with pagination
      - |__ subqueryload: Legacy subquery loader, superseded by selectinload in 2.0

---

### [ ] Topic 8. Advanced SQL: Aggregations, Grouping, CTEs, Window Functions & Bulk DML

- [ ] **Box 1: Aggregations & Grouping**
  - |__ **SQL Functions & Grouping**
      - |__ `func.count()`, `func.sum()`, `func.avg()`, `func.max()`, `func.min()`
      - |__ Group by & Having: `select(User.department, func.count(User.id)).group_by(User.department).having(func.count(User.id) > 10)`
      - |__ Conditional aggregations: `func.count().filter(User.is_active == True)`

- [ ] **Box 2: Common Table Expressions (CTEs) & Window Functions**
  - |__ **Complex Querying**
      - |__ CTE: `cte = select(Order).where(...).cte("filtered_orders")`
      - |__ Recursive CTE: `cte = base_query.cte("hierarchy", recursive=True)` for deep tree traversal
      - |__ Window functions: `func.row_number().over(partition_by=Employee.dept_id, order_by=Employee.salary.desc())`
      - |__ CASE expressions: `case((User.score >= 90, 'A'), (User.score >= 80, 'B'), else_='C')`

- [ ] **Box 3: 2.0 Bulk DML Operations**
  - |__ **Bulk Insert, Update & Delete**
      - |__ Bulk Insert: `insert(User).values([...])` with `.returning(User.id)`
      - |__ Bulk Update: `update(User).where(User.status == 'pending').values(status='active')`
      - |__ Bulk Delete: `delete(User).where(User.is_active == False)`

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Advanced SQL Traps**
      - |__ Trap 1: Bulk `update()` bypasses Python ORM event hooks and session object state (session objects remain stale in memory without `synchronize_session='fetch'`)
      - |__ Trap 2: Omitting `.returning()` on bulk inserts when database-generated IDs are needed

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **SQLAlchemy Dialect Compiler AST**
      - |__ Compiling CTE structures and window frame specifications into database-specific SQL strings

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **ORM Session CRUD vs Bulk DML Statements**
      - |__ Session CRUD: Hydrates Python objects, tracks unit of work, runs hooks, slow for 10,000+ rows
      - |__ Bulk DML: Executes direct single SQL statement in DB, 100x faster, no object hydration

---

### [ ] Topic 9. Asynchronous SQLAlchemy (AsyncEngine, AsyncSession & Greenlet Mechanics)

- [ ] **Box 1: Async Engine & Session Setup**
  - |__ **Async Architecture**
      - |__ Async drivers: `postgresql+asyncpg://` or `sqlite+aiosqlite://`
      - |__ Async Engine: `create_async_engine(url, echo=False)`
      - |__ Async Session Factory: `async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)`

- [ ] **Box 2: Async Query Execution & Lazy-Loading Restrictions**
  - |__ **Async CRUD**
      - |__ Execution: `result = await session.execute(stmt)` and `items = result.scalars().all()`
      - |__ Async get: `user = await session.get(User, user_id)`
      - |__ The Greenlet Limitation: Implicit lazy loading is PROHIBITED in async mode; accessing unloaded relation raises `MissingGreenlet` error!
      - |__ Mandatory explicit loading: Must ALWAYS use `selectinload` or `joinedload` on relationships in async code

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Async Traps**
      - |__ Trap 1: `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called`: Triggered by touching an unloaded relationship outside greenlet context in async!
      - |__ Trap 2: Using synchronous DBAPI drivers (`psycopg2`) with `create_async_engine` crashing on startup

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Greenlet Async Bridge (greenlet_spawn)**
      - |__ How SQLAlchemy executes synchronous-like internal ORM state code over asyncio event loops using greenlet micro-threads

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Sync Session vs AsyncSession**
      - |__ Sync: Simple, traditional, blocks thread during DB I/O (requires threadpool in FastAPI)
      - |__ Async: Native event loop integration, handles 10,000+ concurrent connections, strict loading discipline required

---

### [ ] Topic 10. Transactions, Savepoints, Event Hooks & Alembic Migrations

- [ ] **Box 1: Transaction Isolation & Savepoints**
  - |__ **Transaction Control**
      - |__ Explicit transaction context: `async with session.begin(): ...` (auto-commit/rollback)
      - |__ Nested transactions / Savepoints: `async with session.begin_nested(): ...`
      - |__ Partial rollback: Rolling back inner savepoint without terminating outer business transaction
      - |__ Isolation levels: `isolation_level="REPEATABLE READ"` or `"SERIALIZABLE"`

- [ ] **Box 2: Event Listeners & Audit Hooks**
  - |__ **SQLAlchemy Event System**
      - |__ `@event.listens_for(Session, "before_commit")`: Validates business invariants before DB write
      - |__ Automatic audit timestamps: `@event.listens_for(Base, "before_insert", propagate=True)` updating `updated_at`
      - |__ Attribute mutation hooks: `@event.listens_for(User.password, "set")` for auto-hashing

- [ ] **Box 3: Database Migrations with Alembic**
  - |__ **Alembic Architecture**
      - |__ `alembic init -t async alembic`: Setting up async migration template
      - |__ `env.py`: Pointing `target_metadata = Base.metadata` to DeclarativeBase model metadata
      - |__ Autogenerate commands: `alembic revision --autogenerate -m "create users"`
      - |__ Upgrades & Downgrades: `alembic upgrade head` and `alembic downgrade -1`

- [ ] **⚡ High-Yield Interview Traps & Pitfalls**
  - |__ **Transaction & Migration Traps**
      - |__ Trap 1: Alembic autogenerate CANNOT detect table renames or column renames (generates DROP + ADD leading to production data wipeouts!)
      - |__ Trap 2: Mutating objects inside `after_commit` event hook: Transaction is already committed, mutations will never be written to DB

- [ ] **✍️ SDE-2 Deep-Dive Internals Frameworks**
  - |__ **Alembic Schema Comparator Engine**
      - |__ Comparing Python MetaData against live PostgreSQL Information_Schema tables

- [ ] **⚖️ Master Comparative Matrix**
  - |__ **Savepoint vs Root Transaction**
      - |__ Root Transaction (`BEGIN/COMMIT`): The ultimate boundary of data durability
      - |__ Savepoint (`SAVEPOINT/ROLLBACK TO`): In-flight partial recovery point within an active transaction
