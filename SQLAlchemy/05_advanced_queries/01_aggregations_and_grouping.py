"""
05. AGGREGATIONS AND GROUPING
=============================
This script demonstrates SQL aggregations and grouping in SQLAlchemy 2.0:
1. Aggregate SQL functions (`func.count()`, `func.sum()`, `func.avg()`, `func.min()`, `func.max()`).
2. Grouping rows using `.group_by()`.
3. Filtering aggregated groups using `.having()`.
"""

from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50))
    amount: Mapped[float] = mapped_column()

def setup_data():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all([
            Order(customer="Alice", category="Electronics", amount=1200),
            Order(customer="Alice", category="Books", amount=45),
            Order(customer="Bob", category="Electronics", amount=850),
            Order(customer="Bob", category="Electronics", amount=300),
            Order(customer="Charlie", category="Books", amount=25),
            Order(customer="Charlie", category="Clothing", amount=150),
            Order(customer="Alice", category="Clothing", amount=200),
        ])
        session.commit()
    return engine

def demo_aggregations(engine):
    with Session(engine) as session:
        print("--- 1. Simple Table-wide Aggregates ---")
        stmt = select(
            func.count(Order.id).label("total_orders"),
            func.sum(Order.amount).label("total_revenue"),
            func.avg(Order.amount).label("average_order_value"),
            func.min(Order.amount).label("min_order"),
            func.max(Order.amount).label("max_order"),
        )
        row = session.execute(stmt).one()
        print(f" Total Orders : {row.total_orders}")
        print(f" Total Revenue: ${row.total_revenue:.2f}")
        print(f" Avg Order Val: ${row.average_order_value:.2f}")
        print(f" Min / Max    : ${row.min_order:.2f} / ${row.max_order:.2f}")

        print("\n--- 2. Group By Category ---")
        stmt = (
            select(
                Order.category,
                func.count(Order.id).label("order_count"),
                func.sum(Order.amount).label("category_revenue"),
            )
            .group_by(Order.category)
            .order_by(func.sum(Order.amount).desc())
        )

        for category, count, revenue in session.execute(stmt):
            print(f" Category '{category}': {count} orders | Total: ${revenue:.2f}")

        print("\n--- 3. Group By Customer with HAVING Clause ---")
        # Find customers whose total spending exceeds $300
        stmt = (
            select(
                Order.customer,
                func.sum(Order.amount).label("total_spent"),
            )
            .group_by(Order.customer)
            .having(func.sum(Order.amount) > 300)
        )

        for customer, total_spent in session.execute(stmt):
            print(f" VIP Customer '{customer}': Spent ${total_spent:.2f}")

if __name__ == "__main__":
    engine = setup_data()
    demo_aggregations(engine)
