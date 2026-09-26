"""
03. LOADING STRATEGIES DEEP DIVE (SQLAlchemy 2.0)
=================================================
This script demonstrates all relationship loading strategies in SQLAlchemy 2.0:
1. Lazy Loading (`lazy="select"`) & The N+1 Query Problem.
2. Eager Loading via `selectinload()` (Best for 1:N and M:N collections).
3. Eager Loading via `joinedload()` (Best for N:1 and 1:1 scalar objects).
4. Eager Loading via `subqueryload()` (Best for nested collections).
5. Explicit Loading via `contains_eager()` (With manual JOIN and WHERE filters).
6. Raise Loading (`lazy="raise"`) - Guardrail against silent N+1 queries in production.
7. Write-Only Loading (`WriteOnlyMapped[T]`) - For huge collections where loading all items is impractical.
"""

from typing import List
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    WriteOnlyMapped,
    contains_eager,
    joinedload,
    mapped_column,
    relationship,
    selectinload,
    subqueryload,
    Session,
)

class Base(DeclarativeBase):
    pass

# Models for testing loading strategies
class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    # Standard Lazy Loading (Default)
    products: Mapped[List["Product"]] = relationship("Product", back_populates="store")

    # Raise loading: Raises error if products_guarded is accessed without explicit eager loading!
    guarded_products: Mapped[List["Product"]] = relationship(
        "Product", lazy="raise", viewonly=True
    )

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    price: Mapped[float] = mapped_column()
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"))

    store: Mapped[Store] = relationship(Store, back_populates="products")

# Model demonstrating WriteOnlyMapped for large collections
class Publisher(Base):
    __tablename__ = "publishers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    # WriteOnlyMapped allows streaming queries over millions of records without loading them into python list!
    articles: WriteOnlyMapped["Article"] = relationship("Article", back_populates="publisher")

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    publisher_id: Mapped[int] = mapped_column(ForeignKey("publishers.id"))

    publisher: Mapped[Publisher] = relationship(Publisher, back_populates="articles")


def seed_data(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        s1 = Store(name="Tech MegaStore")
        s2 = Store(name="Book Haven")

        p1 = Product(name="Laptop", price=1200, store=s1)
        p2 = Product(name="Smartphone", price=800, store=s1)
        p3 = Product(name="Headphones", price=150, store=s1)
        p4 = Product(name="Novel", price=20, store=s2)
        p5 = Product(name="Cookbook", price=35, store=s2)

        pub = Publisher(name="Tech Publishing House")
        for i in range(100):
            pub.articles.add(Article(title=f"Article #{i+1}"))

        session.add_all([s1, s2, p1, p2, p3, p4, p5, pub])
        session.commit()

def demo_loading_strategies():
    engine = create_engine("sqlite:///:memory:", echo=False)
    seed_data(engine)

    print("=================================================================")
    print("--- 1. LAZY LOADING (N+1 Problem) ---")
    print("=================================================================")
    with Session(engine) as session:
        # Query stores (Query 1)
        stores = session.scalars(select(Store)).all()
        print(f"Fetched {len(stores)} stores.")
        # Accessing .products on each store executes an EXTRA query per store (Queries 2 & 3!)
        for s in stores:
            print(f" Store '{s.name}' has {len(s.products)} products (Lazy Loaded).")

    print("\n=================================================================")
    print("--- 2. SELECTINLOAD (Best for Collections / 1:N / M:N) ---")
    print("=================================================================")
    # Emits 2 queries total: 1 for Stores, 1 for Products using WHERE store_id IN (1, 2)
    with Session(engine) as session:
        stmt = select(Store).options(selectinload(Store.products))
        stores = session.scalars(stmt).all()
        for s in stores:
            print(f" Store '{s.name}' has {len(s.products)} products (Selectin Loaded).")

    print("\n=================================================================")
    print("--- 3. JOINEDLOAD (Best for Scalar Many-to-One / One-to-One) ---")
    print("=================================================================")
    # Emits 1 single query using LEFT OUTER JOIN
    with Session(engine) as session:
        stmt = select(Product).options(joinedload(Product.store))
        products = session.scalars(stmt).all()
        for p in products:
            print(f" Product '{p.name}' belongs to Store '{p.store.name}' (Joined Loaded).")

    print("\n=================================================================")
    print("--- 4. CONTAINS_EAGER (Eager population with explicit JOIN) ---")
    print("=================================================================")
    # Allows filtering on Store attributes while populating Product.store relationship eager context
    with Session(engine) as session:
        stmt = (
            select(Product)
            .join(Product.store)
            .where(Store.name == "Tech MegaStore")
            .options(contains_eager(Product.store))
        )
        tech_products = session.scalars(stmt).all()
        for p in tech_products:
            print(f" Tech Product: {p.name} (${p.price}) | Store: {p.store.name}")

    print("\n=================================================================")
    print("--- 5. RAISE LOADING (Preventing accidental N+1 queries) ---")
    print("=================================================================")
    with Session(engine) as session:
        store = session.scalars(select(Store).where(Store.id == 1)).one()
        try:
            # Accessing guarded_products without selectinload raises InvalidRequestError!
            _ = store.guarded_products
        except Exception as e:
            print(f" ✓ Successfully caught raise loading exception:\n   [{type(e).__name__}]: {e}")

    print("\n=================================================================")
    print("--- 6. WRITE-ONLY LOADING (For Huge Collections) ---")
    print("=================================================================")
    with Session(engine) as session:
        pub = session.scalars(select(Publisher).where(Publisher.name == "Tech Publishing House")).one()
        # pub.articles is NOT a Python list! It is a query builder.
        # We can issue count(), filter, or limit queries directly on the database:
        count_stmt = select(Publisher).where(Publisher.id == pub.id)
        # Query articles with limit & filter
        articles_stmt = pub.articles.select().where(Article.title.like("%#1%")).limit(5)
        articles = session.scalars(articles_stmt).all()
        print(f" Queried first 5 matching articles from 100 bulk items: {[a.title for a in articles]}")

if __name__ == "__main__":
    demo_loading_strategies()
