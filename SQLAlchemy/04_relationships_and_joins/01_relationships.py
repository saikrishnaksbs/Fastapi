"""
04. RELATIONSHIPS (1-to-Many, Many-to-1, 1-to-1, Many-to-Many)
============================================================
This script demonstrates how to define relationships in SQLAlchemy 2.0:
1. One-to-Many & Many-to-One (`ForeignKey`, `relationship`, `back_populates`).
2. One-to-One (`uselist=False` or scalar annotation).
3. Many-to-Many using an Association Table (`Secondary`).
4. Cascade behaviors (`cascade="all, delete-orphan"`).
"""

from typing import List, Optional
from sqlalchemy import Column, ForeignKey, Table, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

class Base(DeclarativeBase):
    pass

# --- MANY-TO-MANY ASSOCIATION TABLE ---
# Association table for Tag <-> Post relationship
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

# --- ONE-TO-ONE PROFILE MODEL ---
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[Optional[str]] = mapped_column(String(255))

    # Foreign Key pointing to User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    user: Mapped["User"] = relationship("User", back_populates="profile")

# --- USER MODEL (ONE-TO-MANY WITH POSTS, ONE-TO-ONE WITH PROFILE) ---
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)

    # One-to-One relationship to UserProfile
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", cascade="all, delete-orphan", uselist=False
    )

    # One-to-Many relationship to Posts
    # If a user is deleted, all their posts are automatically deleted via cascade
    posts: Mapped[List["Post"]] = relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}'>"

# --- POST MODEL (MANY-TO-ONE WITH USER, MANY-TO-MANY WITH TAGS) ---
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)

    # Many-to-One Foreign Key
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    author: Mapped["User"] = relationship("User", back_populates="posts")

    # Many-to-Many relationship to Tag via post_tags association table
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary=post_tags, back_populates="posts"
    )

    def __repr__(self) -> str:
        return f"<Post id={self.id} title='{self.title}'>"

# --- TAG MODEL (MANY-TO-MANY WITH POSTS) ---
class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)

    posts: Mapped[List["Post"]] = relationship(
        "Post", secondary=post_tags, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag '{self.name}'>"


def demo_relationships():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create user with profile
        user = User(username="alice", profile=UserProfile(bio="Python Enthusiast"))

        # Create tags
        python_tag = Tag(name="Python")
        db_tag = Tag(name="Database")

        # Create posts and associate tags
        post1 = Post(title="Learning SQLAlchemy 2.0", tags=[python_tag, db_tag])
        post2 = Post(title="Building FastAPI Apps", tags=[python_tag])

        # Link posts to user
        user.posts.extend([post1, post2])

        session.add(user)
        session.commit()
        print("✓ Created User, Profile, Posts, and Tags in a single commit!")

    # Verify bidirectional navigation
    with Session(engine) as session:
        fetched_user = session.get(User, 1)
        print(f"\nFetched User: {fetched_user}")
        print(f" User Profile Bio: {fetched_user.profile.bio if fetched_user.profile else None}")
        print(f" User Posts Count: {len(fetched_user.posts)}")

        for p in fetched_user.posts:
            print(f"   - Post '{p.title}' Tags: {[t.name for t in p.tags]}")

        # Cascade Delete Test
        print("\n--- Testing Cascade Delete ---")
        session.delete(fetched_user)
        session.commit()

        # Check if posts were deleted
        remaining_posts = session.query(Post).all()
        print(f"Remaining Posts after User delete: {remaining_posts}")  # []

if __name__ == "__main__":
    demo_relationships()
