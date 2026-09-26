"""
07. TRANSACTIONS, SAVEPOINTS, AND EVENT LISTENERS
=================================================
This script demonstrates transaction management and event hooks in SQLAlchemy 2.0:
1. Savepoints / Nested Transactions (`session.begin_nested()`).
2. Event listeners (`event.listen()` and `@event.listens_for`).
3. Automatic timestamp auditing (`before_insert`, `before_update`).
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, String, create_engine, event, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

class AuditMixin:
    """Mixin class providing automatic timestamp auditing fields."""
    created_at: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)

class Account(Base, AuditMixin):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(String(50))
    balance: Mapped[float] = mapped_column()

# --- EVENT LISTENERS FOR AUTOMATIC AUDITING ---
@event.listens_for(Account, "before_insert")
def set_created_at(mapper, connection, target):
    """Automatically populate created_at & updated_at timestamps prior to INSERT."""
    now = datetime.now(timezone.utc)
    target.created_at = now
    target.updated_at = now
    print(f"[EVENT LOG] before_insert hook triggered for account: {target.owner}")

@event.listens_for(Account, "before_update")
def set_updated_at(mapper, connection, target):
    """Automatically update updated_at timestamp prior to UPDATE."""
    target.updated_at = datetime.now(timezone.utc)
    print(f"[EVENT LOG] before_update hook triggered for account: {target.owner}")


def demo_savepoints_and_events():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        print("--- 1. Testing Event Hooks on Insert ---")
        acc1 = Account(owner="Alice", balance=500.0)
        acc2 = Account(owner="Bob", balance=300.0)

        session.add_all([acc1, acc2])
        session.commit()

        print(f" Alice Created At: {acc1.created_at}")

        print("\n--- 2. Savepoints / Nested Transactions ---")
        # Start main outer transaction
        with session.begin_nested():  # SAVEPOINT 1
            print(" In Savepoint: Deducting $100 from Alice...")
            acc1.balance -= 100.0

            # Imagine a second operation fails
            try:
                with session.begin_nested():  # SAVEPOINT 2
                    acc2.balance += 100.0
                    # Simulate an unexpected error during processing!
                    raise RuntimeError("Payment Gateway Error!")
            except RuntimeError as e:
                print(f" Error caught in nested savepoint: {e}")
                print(" Inner savepoint rolled back automatically! Main transaction continues.")

        session.commit()

        # Check balances: Alice was deducted, but Bob wasn't credited due to savepoint rollback!
        refreshed_alice = session.get(Account, 1)
        refreshed_bob = session.get(Account, 2)
        print(f" Final Alice Balance: ${refreshed_alice.balance}")
        print(f" Final Bob Balance: ${refreshed_bob.balance}")

if __name__ == "__main__":
    demo_savepoints_and_events()
