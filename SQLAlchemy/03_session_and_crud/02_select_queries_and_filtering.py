"""
03. SELECT QUERIES AND FILTERING (SQLAlchemy 2.0 Style)
========================================================
This script demonstrates querying data in SQLAlchemy 2.0:
1. `select()` statement construction.
2. Filtering methods: `.where()`, `.filter_by()`.
3. Logical conditions: `and_()`, `or_()`, `not_()`, `in_()`, `like()`, `ilike()`.
4. Sorting (`order_by()`, `desc()`) & Pagination (`limit()`, `offset()`).
5. Fetching scalar results: `session.scalars()`, `scalar_one()`, `scalar_one_or_none()`, `all()`, `first()`.
"""

from typing import Optional
from sqlalchemy import (
    String,
    and_,
    create_engine,
    desc,
    in_,
    not_,
    or_,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    department: Mapped[str] = mapped_column(String(50))
    salary: Mapped[float] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f"<Emp({self.name}, dept='{self.department}', salary=${self.salary}, active={self.is_active})>"

# Seed initial data
engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add_all([
        Employee(name="Alice", department="Engineering", salary=95000, is_active=True),
        Employee(name="Bob", department="Engineering", salary=80000, is_active=True),
        Employee(name="Charlie", department="Marketing", salary=65000, is_active=False),
        Employee(name="David", department="Sales", salary=75000, is_active=True),
        Employee(name="Eve", department="Engineering", salary=110000, is_active=True),
    ])
    session.commit()

def demo_queries():
    with Session(engine) as session:
        print("--- 1. Simple Select & scalars().all() ---")
        # In 2.0, construct select(Model) and pass to session.scalars()
        stmt = select(Employee)
        employees = session.scalars(stmt).all()
        for emp in employees:
            print(" ", emp)

        print("\n--- 2. Filtering with .where() & Logical Operators ---")
        # Find active Engineering employees earning > $85,000
        stmt = (
            select(Employee)
            .where(
                and_(
                    Employee.department == "Engineering",
                    Employee.salary > 85000,
                    Employee.is_active.is_(True)
                )
            )
        )
        high_earners = session.scalars(stmt).all()
        print("High Earning Engineers:", high_earners)

        print("\n--- 3. Using OR and IN Clause ---")
        # Find employees in Marketing OR Sales, OR with salary in list
        stmt = select(Employee).where(
            or_(
                Employee.department.in_(["Marketing", "Sales"]),
                Employee.name.ilike("a%")  # Case-insensitive LIKE search
            )
        )
        matched = session.scalars(stmt).all()
        print("Matched OR / IN query:", matched)

        print("\n--- 4. Ordering & Pagination (Limit / Offset) ---")
        # Sort by salary descending, skip top 1, get next 2
        stmt = (
            select(Employee)
            .order_by(desc(Employee.salary))
            .offset(1)
            .limit(2)
        )
        paginated = session.scalars(stmt).all()
        print("Paginated Result (Rank 2 & 3 salaries):", paginated)

        print("\n--- 5. Fetching Single Result Helpers ---")
        # scalar_one_or_none(): returns single record or None if not found (raises Exception if multiple found)
        alice = session.scalars(
            select(Employee).where(Employee.name == "Alice")
        ).scalar_one_or_none()
        print("Fetched Alice:", alice)

        missing = session.scalars(
            select(Employee).where(Employee.name == "Ghost")
        ).scalar_one_or_none()
        print("Fetched Missing User:", missing)  # None

if __name__ == "__main__":
    demo_queries()
