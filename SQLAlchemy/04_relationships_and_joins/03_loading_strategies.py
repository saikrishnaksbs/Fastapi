"""
04. RELATIONSHIP LOADING STRATEGIES (N+1 Query Prevention)
==========================================================
This script demonstrates how to solve the infamous N+1 problem in ORMs:
1. Lazy Loading (Default `lazy="select"`) - triggers separate query per relationship access.
2. `selectinload()` - Eager loading using SELECT IN query (Best for 1-to-Many).
3. `joinedload()` - Eager loading using LEFT OUTER JOIN (Best for Many-to-1 / 1-to-1).
4. `subqueryload()` - Eager loading using subquery.
5. `contains_eager()` - Populates relationships using manual explicit joins.
"""

from typing import List
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    contains_eager,
    joinedload,
    mapped_column,
    relationship,
    selectinload,
    Session,
)

class Base(DeclarativeBase):
    pass

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="company")

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))

    company: Mapped[Company] = relationship("Company", back_populates="employees")

def seed_data(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        c1 = Company(name="TechCorp")
        c2 = Company(name="FinTech Inc")

        c1.employees.extend([Employee(name="Alice"), Employee(name="Bob"), Employee(name="Charlie")])
        c2.employees.extend([Employee(name="David"), Employee(name="Eve")])

        session.add_all([c1, c2])
        session.commit()

def demo_loading_strategies():
    # Enable echo=True to see exact SQL queries executed!
    engine = create_engine("sqlite:///:memory:", echo=True)
    seed_data(engine)

    print("\n=======================================================")
    print("--- 1. SELECTINLOAD (Best for 1-to-Many collections) ---")
    print("=======================================================")
    # Executes 2 queries total: 1 for companies, 1 SELECT IN for all employees
    with Session(engine) as session:
        stmt = select(Company).options(selectinload(Company.employees))
        companies = session.scalars(stmt).all()
        for c in companies:
            print(f"Company '{c.name}' has {len(c.employees)} employees")

    print("\n=======================================================")
    print("--- 2. JOINEDLOAD (Best for Many-to-1 scalar objects) ---")
    print("=======================================================")
    # Executes 1 single query using LEFT OUTER JOIN
    with Session(engine) as session:
        stmt = select(Employee).options(joinedload(Employee.company))
        employees = session.scalars(stmt).all()
        for emp in employees:
            print(f"Employee '{emp.name}' works at '{emp.company.name}'")

    print("\n=======================================================")
    print("--- 3. CONTAINS_EAGER (When manually filtering on joined table) ---")
    print("=======================================================")
    # Allows filtering on Company while populating Company relationship eager context
    with Session(engine) as session:
        stmt = (
            select(Employee)
            .join(Employee.company)
            .where(Company.name == "TechCorp")
            .options(contains_eager(Employee.company))
        )
        tech_employees = session.scalars(stmt).all()
        for emp in tech_employees:
            print(f"TechCorp Emp: {emp.name}")

if __name__ == "__main__":
    demo_loading_strategies()
