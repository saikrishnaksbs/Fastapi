# Comprehensive Guide to SQLAlchemy 2.0 Relationships & Loading Strategies

This guide provides an architectural breakdown of every relationship pattern and loading strategy available in SQLAlchemy 2.0.

---

## 🔀 Part 1: Standard Relationship Patterns

| Relationship Type | Foreign Key Location | `relationship()` Config | Key Parameters |
| :--- | :--- | :--- | :--- |
| **One-to-One (1:1)** | Child Table | `relationship("Child", uselist=False)` | `uselist=False`, `ForeignKey(unique=True)` |
| **One-to-Many (1:N)** | Child Table | `relationship("Child", back_populates="parent")` | `cascade="all, delete-orphan"` |
| **Many-to-One (N:1)** | Parent/Child Table | `relationship("Parent", back_populates="children")` | `ForeignKey(...)` |
| **Many-to-Many (M:N)** | Association Table | `relationship("Target", secondary=assoc_table)` | `secondary=assoc_table` |
| **Association Object** | Association Model | `relationship("AssocModel", back_populates=...)` | Extra payload columns (`grade`, `date`) |

---

## 🔄 Part 2: Self-Referential Relationship Patterns

Models that reference themselves in the same database table require explicit `remote_side` or `primaryjoin`/`secondaryjoin` configuration.

### 1. Self-Referential One-to-One (1:1)
* **Use Case**: Peer Mentorship, Partner System, Executive Buddy Assignment.
* **Key Syntax**:
  ```python
  mentor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), unique=True)
  mentor: Mapped[Optional["User"]] = relationship("User", remote_side=[id], uselist=False)
  ```

### 2. Self-Referential One-to-Many (1:N)
* **Use Case**: Organizational Hierarchy (Manager -> Subordinates), Nested Comment Threads, Category Trees.
* **Key Syntax**:
  ```python
  manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"))
  manager: Mapped[Optional["Employee"]] = relationship("Employee", remote_side=[id], back_populates="subordinates")
  subordinates: Mapped[List["Employee"]] = relationship("Employee", back_populates="manager")
  ```

### 3. Self-Referential Many-to-Many (M:N)
* **Use Case**: Social Networks (Followers <-> Following Graph), Related Article Recommendations.
* **Key Syntax**:
  ```python
  following: Mapped[List["User"]] = relationship(
      "User",
      secondary=user_followers_table,
      primaryjoin=(id == user_followers_table.c.user_id),
      secondaryjoin=(id == user_followers_table.c.follower_id),
      back_populates="followers"
  )
  ```

---

## ⚡ Part 3: Relationship Loading Strategies Comparison

| Loading Strategy | SQL Execution | Best Used For | Pros / Cons |
| :--- | :--- | :--- | :--- |
| **`lazy="select"`** (Lazy) | Triggered on attribute access | Default fallback | ⚠️ Causes **N+1 Query Bugs** if accessed in loops! |
| **`selectinload()`** (Eager) | 2 SQL queries (`WHERE id IN (...)`) | Collections (1:N, M:N) | 🚀 Highly efficient, avoids duplicate rows in memory. |
| **`joinedload()`** (Eager) | 1 SQL query (`LEFT OUTER JOIN`) | Scalars (N:1, 1:1) | ⚡ Fast single query; avoid for large collections to prevent Cartesian product explosion. |
| **`subqueryload()`** (Eager) | 2 SQL queries (subquery statement) | Deeply nested collections | Good alternative when `selectinload` IN clause hits DB limit. |
| **`contains_eager()`** | 1 SQL query with explicit `.join()` | Eager loading with `.where()` filters | 🎯 Allows filtering parent models by child attributes while populating relationships. |
| **`lazy="raise"`** | Throws Python error on access | Production APIs & Microservices | 🛡️ Best practice guardrail against silent N+1 query regressions. |
| **`WriteOnlyMapped[T]`** | No auto-fetch (Returns Query object) | Huge collections (10k+ rows) | 📦 Memory efficient; allows calling `.select()`, `.where()`, `.limit()` on relationships. |

---

## 💻 Summary Recommendation Matrix

* For **FastAPI APIs & REST Endpoints**: Always use `selectinload()` for list/collection relationships and `joinedload()` for single nested object relationships.
* For **Async SQLAlchemy (`AsyncSession`)**: Always use `selectinload()` or `joinedload()` because standard lazy loading is blocked in async context.
* For **High-Volume Tables**: Use `WriteOnlyMapped[T]` to paginate child collections directly on the database.
