"""
05. SUBQUERIES, CTES, WINDOW FUNCTIONS, AND CASE STATEMENTS
===========================================================
This script demonstrates advanced SQL relational constructs:
1. Subqueries (`.subquery()`).
2. Common Table Expressions (`.cte()`).
3. Window Functions (`func.row_number().over()`, `func.rank().over()`).
4. Conditional logic using `case()`.
"""

from sqlalchemy import String, case, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    department: Mapped[str] = mapped_column(String(50))
    salary: Mapped[float] = mapped_column()

def setup_data():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all([
            Employee(name="Alice", department="Engineering", salary=120000),
            Employee(name="Bob", department="Engineering", salary=90000),
            Employee(name="Charlie", department="Engineering", salary=95000),
            Employee(name="David", department="Marketing", salary=70000),
            Employee(name="Eve", department="Marketing", salary=85000),
            Employee(name="Frank", department="Sales", salary=60000),
        ])
        session.commit()
    return engine

def demo_advanced_sql(engine):
    with Session(engine) as session:
        print("--- 1. Subquery: Employees earning above average salary ---")
        # Step A: Subquery for overall average salary
        avg_salary_subq = select(func.avg(Employee.salary)).scalar_subquery()

        # Step B: Main query comparing salary > average salary
        stmt = select(Employee.name, Employee.salary).where(
            Employee.salary > avg_salary_subq
        )

        for name, salary in session.execute(stmt):
            print(f" Above Avg Salary: {name} (${salary:.2f})")

        print("\n--- 2. Common Table Expression (CTE) ---")
        # Define a CTE calculating average salary per department
        dept_avg_cte = (
            select(
                Employee.department.label("dept"),
                func.avg(Employee.salary).label("avg_dept_salary"),
            )
            .group_by(Employee.department)
            .cte("dept_avg_cte")
        )

        # Join main query against the CTE
        stmt = select(
            Employee.name,
            Employee.department,
            Employee.salary,
            dept_avg_cte.c.avg_dept_salary,
        ).join(dept_avg_cte, Employee.department == dept_avg_cte.c.dept)

        for name, dept, salary, dept_avg in session.execute(stmt):
            print(f" {name} ({dept}): ${salary:.2f} | Dept Avg: ${dept_avg:.2f}")

        print("\n--- 3. Window Function: Salary Rank within Department ---")
        rank_window = func.rank().over(
            partition_by=Employee.department, order_by=Employee.salary.desc()
        )

        stmt = select(
            Employee.name,
            Employee.department,
            Employee.salary,
            rank_window.label("dept_salary_rank"),
        )

        for name, dept, salary, rank in session.execute(stmt):
            print(f" {dept} Rank #{rank}: {name} (${salary:.2f})")

        print("\n--- 4. Conditional CASE Statement ---")
        salary_tier = case(
            (Employee.salary >= 100000, "High Tier"),
            (Employee.salary >= 80000, "Mid Tier"),
            else_="Standard Tier",
        ).label("tier")

        stmt = select(Employee.name, Employee.salary, salary_tier)

        for name, salary, tier in session.execute(stmt):
            print(f" {name} (${salary:.2f}) -> {tier}")

if __name__ == "__main__":
    engine = setup_data()
    demo_advanced_sql(engine)
