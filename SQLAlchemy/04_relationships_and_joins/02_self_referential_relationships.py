"""
02. SELF-REFERENTIAL RELATIONSHIPS (SQLAlchemy 2.0)
===================================================
This script demonstrates self-referential relationships (models that reference themselves):
1. Self-Referential One-to-One (1:1) - Peer Mentor & Mentee system (`remote_side`, `uselist=False`).
2. Self-Referential One-to-Many (1:N) - Organizational Manager & Subordinates hierarchy (`remote_side`).
3. Self-Referential Many-to-Many (M:N) - Social Network Followers & Following graph (`primaryjoin`, `secondaryjoin`).
"""

from typing import List, Optional
from sqlalchemy import Column, ForeignKey, Table, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

class Base(DeclarativeBase):
    pass

# =====================================================================
# PATTERN 1: SELF-REFERENTIAL ONE-TO-ONE (1:1)
# =====================================================================
# A Peer Mentor has exactly one Mentee, and a Mentee has exactly one Mentor.

class PeerUser(Base):
    __tablename__ = "peer_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    # Foreign key referencing another user in the SAME table
    mentor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("peer_users.id", ondelete="SET NULL"), unique=True
    )

    # Self-referential 1:1 relationship
    # `remote_side=[id]` tells SQLAlchemy that `mentor_id` points to `id` on the remote side
    mentor: Mapped[Optional["PeerUser"]] = relationship(
        "PeerUser",
        remote_side=[id],
        back_populates="mentee",
        uselist=False,
    )
    mentee: Mapped[Optional["PeerUser"]] = relationship(
        "PeerUser",
        back_populates="mentor",
        uselist=False,
    )


# =====================================================================
# PATTERN 2: SELF-REFERENTIAL ONE-TO-MANY (1:N)
# =====================================================================
# A Manager has Many Subordinates (1:N). A Subordinate reports to One Manager (N:1).

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(50))

    # Foreign Key pointing to Manager's id in the same table
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Many-to-One: Employee -> Manager (Scalar object)
    # `remote_side=[id]` specifies that manager_id references id
    manager: Mapped[Optional["Employee"]] = relationship(
        "Employee", remote_side=[id], back_populates="subordinates"
    )

    # One-to-Many: Manager -> Subordinates (List of objects)
    subordinates: Mapped[List["Employee"]] = relationship(
        "Employee", back_populates="manager"
    )


# =====================================================================
# PATTERN 3: SELF-REFERENTIAL MANY-TO-MANY (M:N)
# =====================================================================
# Social Network Graph: User Followers & Following.
# Uses a self-referential association table with explicit primaryjoin & secondaryjoin.

followers_association = Table(
    "user_followers",
    Base.metadata,
    Column("user_id", ForeignKey("social_users.id", ondelete="CASCADE"), primary_key=True),
    Column("follower_id", ForeignKey("social_users.id", ondelete="CASCADE"), primary_key=True),
)

class SocialUser(Base):
    __tablename__ = "social_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)

    # People who this user is FOLLOWING:
    # primaryjoin: user_id == self.id (The user doing the following)
    # secondaryjoin: follower_id == SocialUser.id (The user being followed)
    following: Mapped[List["SocialUser"]] = relationship(
        "SocialUser",
        secondary=followers_association,
        primaryjoin=(id == followers_association.c.user_id),
        secondaryjoin=(id == followers_association.c.follower_id),
        back_populates="followers",
    )

    # People who are FOLLOWING this user:
    followers: Mapped[List["SocialUser"]] = relationship(
        "SocialUser",
        secondary=followers_association,
        primaryjoin=(id == followers_association.c.follower_id),
        secondaryjoin=(id == followers_association.c.user_id),
        back_populates="following",
    )


# =====================================================================
# DEMONSTRATION & VERIFICATION
# =====================================================================
def run_demo():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        print("--- 1. Self-Referential 1:1 (Peer Mentorship) ---")
        senior = PeerUser(name="Alice (Senior Dev)")
        junior = PeerUser(name="Bob (Junior Dev)", mentor=senior)

        session.add_all([senior, junior])
        session.commit()

        print(f" Junior '{junior.name}' -> Mentor: '{junior.mentor.name}'")
        print(f" Senior '{senior.name}' -> Mentee: '{senior.mentee.name}'")

        print("\n--- 2. Self-Referential 1:N (Org Hierarchy) ---")
        ceo = Employee(name="Sarah", title="CEO")
        session.add(ceo)
        session.flush()

        cto = Employee(name="Michael", title="CTO", manager=ceo)
        cpo = Employee(name="Rachel", title="CPO", manager=ceo)
        session.add_all([cto, cpo])
        session.flush()

        dev1 = Employee(name="Dave", title="Lead Engineer", manager=cto)
        dev2 = Employee(name="Eve", title="Backend Engineer", manager=cto)
        session.add_all([dev1, dev2])
        session.commit()

        print(f" CEO '{ceo.name}' Direct Reports: {[e.name for e in ceo.subordinates]}")
        print(f" CTO '{cto.name}' Direct Reports: {[e.name for e in cto.subordinates]}")
        print(f" Dev '{dev2.name}' Reports Up To: '{dev2.manager.name}' (Manager's Manager: '{dev2.manager.manager.name}')")

        print("\n--- 3. Self-Referential M:N (Followers Graph) ---")
        u1 = SocialUser(username="@elon")
        u2 = SocialUser(username="@shiva")
        u3 = SocialUser(username="@todd")

        session.add_all([u1, u2, u3])
        session.commit()

        # @shiva and @todd follow @elon
        u2.following.append(u1)
        u3.following.append(u1)
        # @elon follows @shiva back
        u1.following.append(u2)

        session.commit()

        print(f" User '{u1.username}' Followers: {[u.username for u in u1.followers]}")
        print(f" User '{u1.username}' Following: {[u.username for u in u1.following]}")
        print(f" User '{u2.username}' Following: {[u.username for u in u2.following]}")

if __name__ == "__main__":
    run_demo()
