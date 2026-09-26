"""
04. JOINS AND ALIASING (SQLAlchemy 2.0 Style)
==============================================
This script demonstrates explicit SQL joins and model aliasing:
1. Inner Join (`select().join()`).
2. Outer Join (`select().outerjoin()`).
3. Explicit join conditions.
4. Model Aliasing (`aliased()`) for joining the same table multiple times (e.g., Self-Referential hierarchies).
"""

from typing import List, Optional
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    aliased,
    mapped_column,
    relationship,
    Session,
)

class Base(DeclarativeBase):
    pass

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="department")

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"))

    department: Mapped[Optional[Department]] = relationship("Department", back_populates="employees")
    manager: Mapped[Optional["Employee"]] = relationship("Employee", remote_side=[id])

def setup_data():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        eng = Department(name="Engineering")
        hr = Department(name="Human Resources")
        exec_dept = Department(name="Executive")

        # Manager
        ceo = Employee(name="Sarah (CEO)", department=exec_dept)
        session.add(ceo)
        session.flush()

        # Employees with manager
        emp1 = Employee(name="Bob", department=eng, manager=ceo)
        emp2 = Employee(name="Alice", department=eng, manager=ceo)
        emp3 = Employee(name="Charlie", department=None, manager=None)  # Unassigned department

        session.add_all([eng, hr, exec_dept, emp1, emp2, emp3])
        session.commit()

    return engine

def demo_joins_and_aliases(engine):
    with Session(engine) as session:
        print("--- 1. Inner Join (Only Employees with a Department) ---")
        # Returns tuples of (Employee.name, Department.name)
        stmt = (
            select(Employee.name, Department.name)
            .join(Employee.department)  # Joins automatically using relationship FK!
        )
        for emp_name, dept_name in session.execute(stmt):
            print(f" Employee: {emp_name} -> Department: {dept_name}")

        print("\n--- 2. Left Outer Join (All Employees, including unassigned) ---")
        stmt = (
            select(Employee.name, Department.name)
            .outerjoin(Employee.department)
        )
        for emp_name, dept_name in session.execute(stmt):
            print(f" Employee: {emp_name} -> Department: {dept_name or 'Unassigned'}")

        print("\n--- 3. Self-Referential Join using aliased() ---")
        # Aliasing Employee table to join Employee (as worker) with Employee (as manager)
        Manager = aliased(Employee, name="manager_alias")

        stmt = (
            select(Employee.name.label("employee_name"), Manager.name.label("manager_name"))
            .outerjoin(Manager, Employee.manager_id == Manager.id)
        )

        for row in session.execute(stmt):
            print(f" Worker: {row.employee_name} | Reports To: {row.manager_name or 'None (Top Level)'}")

if __name__ == "__main__":
    engine = setup_data()
    demo_joins_and_aliases(engine)
