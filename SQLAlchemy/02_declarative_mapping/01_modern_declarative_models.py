"""
02. MODERN DECLARATIVE MAPPING (SQLAlchemy 2.0 Style)
=====================================================
This script demonstrates the modern SQLAlchemy 2.0 Declarative Mapping syntax:
1. Subclassing `DeclarativeBase`.
2. Defining columns using `Mapped[T]` type annotations and `mapped_column()`.
3. Setting up field constraints: Primary Keys, Indexes, Nullability, Defaults.
4. Python Enums and JSON data types.
"""

from datetime import datetime, timezone
import enum
from typing import Optional
from sqlalchemy import (
    DateTime,
    Enum,
    Integer,
    JSON,
    String,
    create_engine,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# 1. Base Class Definition (SQLAlchemy 2.0 style)
# In 2.0, we inherit from `DeclarativeBase` instead of using legacy `declarative_base()`.
class Base(DeclarativeBase):
    pass

# Enum for user roles
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

# 2. Modern Model Mapping
class User(Base):
    __tablename__ = "users"

    # Primary key with autoincrement
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # String column with max_length=50, indexed and non-nullable
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # Optional column (typing.Optional translates to nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(255), default=None)

    # Python Enum data type
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False
    )

    # JSON payload storage
    settings: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Automatic Server Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Custom string representation for easy debugging
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


# Demonstration
if __name__ == "__main__":
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Create all tables defined under Base
    Base.metadata.create_all(engine)
    print("✓ Tables created successfully via Base.metadata.create_all(engine)")

    with Session(engine) as session:
        new_user = User(
            username="john_doe",
            bio="Software Developer & Tech Enthusiast",
            role=UserRole.ADMIN,
            settings={"theme": "dark", "notifications": True},
        )
        session.add(new_user)
        session.commit()

        # Query user back
        fetched_user = session.get(User, 1)
        print(f"Fetched User: {fetched_user}")
        print(f"User Settings JSON: {fetched_user.settings}")
