"""
06. ASYNC SQLALCHEMY (AsyncEngine & AsyncSession)
=================================================
This script demonstrates asynchronous database access with SQLAlchemy 2.0:
1. `create_async_engine()` with async drivers (e.g. `sqlite+aiosqlite` or `postgresql+asyncpg`).
2. `async_sessionmaker` and `AsyncSession`.
3. `await session.execute()` and `await session.scalars()`.
4. Asynchronous relationship loading using `selectinload()`.
"""

import asyncio
from typing import List
from sqlalchemy import ForeignKey, String, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

class Base(DeclarativeBase):
    pass

class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    books: Mapped[List["Book"]] = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))

    author: Mapped[Author] = relationship("Author", back_populates="books")

# 1. Initialize Async Engine
# SQLite async driver: aiosqlite
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

# 2. Async Sessionmaker Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def main():
    # Create tables asynchronously
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Async DB Tables created successfully.")

    # 3. Async Insert & Commit
    async with AsyncSessionLocal() as session:
        author1 = Author(name="J.K. Rowling")
        author1.books.extend([
            Book(title="Harry Potter and the Philosopher's Stone"),
            Book(title="Harry Potter and the Chamber of Secrets"),
        ])

        author2 = Author(name="J.R.R. Tolkien")
        author2.books.append(Book(title="The Hobbit"))

        session.add_all([author1, author2])
        await session.commit()
        print("✓ Async Data seeded.")

    # 4. Async Query Execution
    async with AsyncSessionLocal() as session:
        # CRITICAL IN ASYNC: Always use selectinload() for relationships in async SQLAlchemy
        # Lazy loading (accessing author.books directly) will raise an MissingGreenlet error in async code!
        stmt = select(Author).options(selectinload(Author.books))

        result = await session.scalars(stmt)
        authors = result.all()

        print("\n--- Async Fetched Authors & Books ---")
        for author in authors:
            print(f" Author: {author.name}")
            for book in author.books:
                print(f"   - Book: {book.title}")

if __name__ == "__main__":
    asyncio.run(main())
