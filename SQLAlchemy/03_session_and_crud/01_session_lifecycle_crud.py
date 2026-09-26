"""
03. SESSION LIFECYCLE AND CRUD OPERATIONS (Unit of Work)
=========================================================
This script demonstrates the SQLAlchemy ORM `Session` and standard CRUD operations:
1. `Session` lifecycle & `sessionmaker`.
2. Unit of Work pattern: track state changes in memory before flushing.
3. CRUD methods: `add()`, `add_all()`, `commit()`, `rollback()`, `flush()`, `refresh()`, `get()`, `delete()`.
"""

from typing import Optional
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', price={self.price}, stock={self.stock})>"

# Setup Database and Session Factory
engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

# `sessionmaker` creates a factory for generating Session objects
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def demo_crud_operations():
    # 1. CREATE (Insert)
    print("--- 1. CREATE Operations ---")
    with SessionLocal() as session:
        # Create single instance
        laptop = Product(name="Laptop", price=1200.0, stock=10)
        session.add(laptop)

        # Bulk add multiple instances
        mouse = Product(name="Wireless Mouse", price=25.0, stock=50)
        keyboard = Product(name="Mechanical Keyboard", price=85.0, stock=30)
        session.add_all([mouse, keyboard])

        # `session.flush()` pushes pending changes to DB without ending transaction.
        # IDs are assigned after flush.
        session.flush()
        print(f"Flushed Laptop ID (before commit): {laptop.id}")

        # `session.commit()` permanently saves transaction to database.
        session.commit()
        print("✓ Products committed successfully.")

    # 2. READ (Fetch by Primary Key)
    print("\n--- 2. READ Operations ---")
    with SessionLocal() as session:
        # `session.get()` is the fastest way to fetch an object by primary key (uses identity map cache)
        item = session.get(Product, 1)
        print(f"Fetched via session.get(Product, 1): {item}")

    # 3. UPDATE (Modify instance)
    print("\n--- 3. UPDATE Operations ---")
    with SessionLocal() as session:
        item = session.get(Product, 1)
        if item:
            item.price = 1100.0  # Discount laptop price
            item.stock += 5
            # SQLAlchemy automatically tracks object mutations! No need to call session.add(item).
            session.commit()
            print(f"Updated Item: {item}")

    # 4. ROLLBACK (Revert uncommitted changes)
    print("\n--- 4. ROLLBACK Operations ---")
    with SessionLocal() as session:
        item = session.get(Product, 1)
        if item:
            item.price = 0.0  # Oops, accidental bad update!
            print(f"Pending dirty state in memory: {item.price}")
            session.rollback()  # Reverts item back to database state
            print(f"After rollback: {item.price}")

    # 5. DELETE (Remove instance)
    print("\n--- 5. DELETE Operations ---")
    with SessionLocal() as session:
        item = session.get(Product, 2)  # Mouse
        if item:
            session.delete(item)
            session.commit()
            print("✓ Mouse deleted successfully.")

        # Verify deletion
        deleted_item = session.get(Product, 2)
        print(f"Fetched deleted mouse: {deleted_item}")  # Returns None

if __name__ == "__main__":
    demo_crud_operations()
