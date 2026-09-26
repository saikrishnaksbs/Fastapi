"""
05. BULK DATA MANIPULATION (DML Statements in 2.0)
==================================================
This script demonstrates high-performance bulk operations in SQLAlchemy 2.0:
1. Bulk `insert()` with values.
2. Bulk `update()` with `.where()`.
3. Bulk `delete()` with `.where()`.
4. Using `.returning()` to inspect modified primary keys/attributes.
"""

from typing import List
from sqlalchemy import String, create_engine, delete, insert, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

class CustomerAccount(Base):
    __tablename__ = "customer_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    balance: Mapped[float] = mapped_column()
    status: Mapped[str] = mapped_column(String(20), default="active")

def demo_bulk_dml():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        print("--- 1. Bulk INSERT with RETURNING ---")
        # In 2.0, insert() can execute high-speed multi-row inserts directly in SQL!
        stmt = insert(CustomerAccount).values([
            {"username": "user1", "balance": 100.0, "status": "active"},
            {"username": "user2", "balance": 250.0, "status": "active"},
            {"username": "user3", "balance": 50.0, "status": "suspended"},
            {"username": "user4", "balance": 500.0, "status": "active"},
        ]).returning(CustomerAccount.id, CustomerAccount.username)

        inserted_rows = session.execute(stmt).all()
        print("Inserted Account IDs & Names:", inserted_rows)
        session.commit()

        print("\n--- 2. Bulk UPDATE (Mass balance increase) ---")
        # Add $50 bonus to all active accounts directly in SQL
        update_stmt = (
            update(CustomerAccount)
            .where(CustomerAccount.status == "active")
            .values(balance=CustomerAccount.balance + 50.0)
            .returning(CustomerAccount.username, CustomerAccount.balance)
        )

        updated_results = session.execute(update_stmt).all()
        print("Updated Accounts:", updated_results)
        session.commit()

        print("\n--- 3. Bulk DELETE ---")
        # Delete all suspended accounts
        delete_stmt = (
            delete(CustomerAccount)
            .where(CustomerAccount.status == "suspended")
            .returning(CustomerAccount.username)
        )

        deleted_users = session.execute(delete_stmt).scalars().all()
        print("Deleted Accounts:", deleted_users)
        session.commit()

        print("\n--- Remaining Accounts in DB ---")
        all_accounts = session.scalars(select(CustomerAccount)).all()
        for acc in all_accounts:
            print(f" Account #{acc.id}: {acc.username} | Balance: ${acc.balance} | Status: {acc.status}")

if __name__ == "__main__":
    demo_bulk_dml()
