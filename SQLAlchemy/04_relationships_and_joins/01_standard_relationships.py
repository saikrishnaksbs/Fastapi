"""
01. STANDARD RELATIONSHIP PATTERNS (SQLAlchemy 2.0)
===================================================
This script provides comprehensive, working examples of standard relationship patterns:
1. One-to-One (1:1) - User & UserProfile
2. One-to-Many (1:N) & Many-to-One (N:1) - Author & Book
3. Many-to-Many (M:N) with standard Association Table - Post & Tag
4. Many-to-Many (M:N) with Association Object Pattern - Student, Course, & Enrollment (with extra payload columns)
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    create_engine,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
)

class Base(DeclarativeBase):
    pass

# =====================================================================
# PATTERN 1: ONE-TO-ONE (1:1)
# =====================================================================
# A User has exactly one Profile, and a Profile belongs to exactly one User.
# Primary key of Profile has unique Foreign Key constraint + uselist=False.

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[Optional[str]] = mapped_column(String(255))

    # Foreign key to User with UNIQUE constraint enforcing 1:1
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="profile")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)

    # uselist=False tells SQLAlchemy this is a single object, not a collection
    profile: Mapped[Optional[Profile]] = relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    # Relationship to Posts (Pattern 2: 1:N)
    posts: Mapped[List["Post"]] = relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )


# =====================================================================
# PATTERN 2: ONE-TO-MANY (1:N) & MANY-TO-ONE (N:1)
# =====================================================================
# A User has Many Posts (1:N). Each Post belongs to One User (N:1).

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    author: Mapped[User] = relationship(User, back_populates="posts")

    # Relationship to Tags (Pattern 3: M:N via secondary)
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary="post_tags", back_populates="posts"
    )


# =====================================================================
# PATTERN 3: MANY-TO-MANY (M:N) via Standard Association Table
# =====================================================================
# A Post has Many Tags; a Tag belongs to Many Posts.
# Uses a simple Table with no extra payload columns.

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    posts: Mapped[List[Post]] = relationship(
        Post, secondary=post_tags, back_populates="tags"
    )


# =====================================================================
# PATTERN 4: MANY-TO-MANY (M:N) via Association Object Pattern
# =====================================================================
# Used when the association table contains EXTRA payload columns
# (e.g. enrollment date, grade, status).

class Enrollment(Base):
    """Association Model between Student and Course containing extra attributes."""
    __tablename__ = "enrollments"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True
    )

    # Extra Payload Columns!
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    grade: Mapped[Optional[float]] = mapped_column(Float, default=None)

    # Relationships back to both parent models
    student: Mapped["Student"] = relationship("Student", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    # Relationship to Association Model
    enrollments: Mapped[List[Enrollment]] = relationship(
        Enrollment, back_populates="student", cascade="all, delete-orphan"
    )

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))

    enrollments: Mapped[List[Enrollment]] = relationship(
        Enrollment, back_populates="course", cascade="all, delete-orphan"
    )


# =====================================================================
# DEMONSTRATION & VERIFICATION
# =====================================================================
def run_demo():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        print("--- 1. Testing 1:1 Relationship ---")
        user = User(username="alice", profile=Profile(bio="Software Engineer"))
        session.add(user)
        session.commit()

        print(f" User: {user.username} <-> Profile Bio: {user.profile.bio}")

        print("\n--- 2. Testing 1:N & M:N (Post & Tags) ---")
        python_tag = Tag(name="Python")
        web_tag = Tag(name="Web")

        post1 = Post(title="SQLAlchemy 2.0 Guide", author=user, tags=[python_tag])
        post2 = Post(title="FastAPI Async Deep Dive", author=user, tags=[python_tag, web_tag])

        session.add_all([post1, post2])
        session.commit()

        print(f" User '{user.username}' has {len(user.posts)} posts.")
        for p in user.posts:
            tag_names = [t.name for t in p.tags]
            print(f"  - Post: '{p.title}' | Tags: {tag_names}")

        print("\n--- 3. Testing M:N Association Object (Enrollment) ---")
        student = Student(name="Bob")
        course1 = Course(title="Database Systems")
        course2 = Course(title="Computer Architecture")

        # Create enrollment association records with extra payload (grade)
        e1 = Enrollment(student=student, course=course1, grade=95.5)
        e2 = Enrollment(student=student, course=course2, grade=88.0)

        session.add_all([student, course1, course2, e1, e2])
        session.commit()

        print(f" Student '{student.name}' Enrollments:")
        for enr in student.enrollments:
            print(f"  - Course: '{enr.course.title}' | Grade: {enr.grade} | Date: {enr.enrolled_at.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    run_demo()
