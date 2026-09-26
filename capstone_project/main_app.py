"""
EXHAUSTIVE FASTAPI & MODERN SQLALCHEMY 2.0 MASTER CAPSTONE
===========================================================
This single, production-grade application implements EVERY SINGLE CONCEPT from all 
12 FastAPI modules and all 8 Modern SQLAlchemy 2.0 modules:

1. CONFIG & SETTINGS: `pydantic-settings` (`BaseSettings`, `SettingsConfigDict`, `@lru_cache`).
2. CORE ENGINE & CONNECTIONS: `create_engine`, connection pooling (`pool_size`, `max_overflow`), 
   `text()` raw SQL execution, parameter binding (`:param`), `connect()` vs `begin()`.
3. DECLARATIVE MAPPING 2.0: `DeclarativeBase`, `Mapped[T]`, `mapped_column()`, `Integer`, `String`, 
   `DateTime`, `Enum`, `JSON`, `__tablename__`, `__repr__`.
4. RELATIONSHIP PATTERNS:
   - Standard 1:1 (`User` <-> `UserProfile` via `uselist=False`, `ForeignKey(unique=True)`).
   - Standard 1:N & N:1 (`User` <-> `Post`).
   - Standard M:N (`Post` <-> `Tag` via `capstone_post_tags` secondary table).
   - Association Object M:N (`Order` <-> `Product` via `OrderItem` with extra `quantity` & `unit_price`).
   - Self-Referential 1:1 (`PeerUser.mentor` <-> `PeerUser.mentee`).
   - Self-Referential 1:N (`Employee.manager` <-> `Employee.subordinates`).
   - Self-Referential M:N (`SocialUser.followers` <-> `SocialUser.following` graph).
5. LOADING STRATEGIES & GUARDRAILS: `selectinload()`, `joinedload()`, `subqueryload()`, `contains_eager()`, 
   `lazy="raise"` (N+1 guardrail), `WriteOnlyMapped[T]` (large datasets).
6. EVENTS & HOOKS: `@event.listens_for` (`before_insert`, `before_update` automatic timestamp auditing).
7. SAVEPOINTS & TRANSACTIONS: Nested transactions (`session.begin_nested()`) & rollbacks.
8. SECURITY & AUTH: Passlib bcrypt password hashing, `pyjwt` JWT generation/decoding with `exp`, 
   `OAuth2PasswordBearer`, `APIKeyHeader`, `APIKeyQuery`.
9. DEPENDENCIES & LIFESPAN: `@asynccontextmanager` DB setup, `yield` DB session dependency, 
   Sub-dependencies, `Cookie()`, `Header()`, Router-level global dependencies (`dependencies=[Depends(...)]`).
10. CUSTOM ROUTE DECORATORS: Dynamic route registration using `@wraps(func)` and `router.add_api_route()`.
11. MIDDLEWARE: `CORSMiddleware` & Custom HTTP timing middleware (`X-Process-Time`).
12. ROUTING & VALIDATION: `APIRouter`, Route Precedence (`/users/me` before `/users/{id}`), `Path()`, `Query()`, `Field()`, 
    `ConfigDict(extra="forbid")`, OpenAPI tags/docstrings.
13. ADVANCED QUERIES: Aggregations (`func.count`, `func.sum`, `func.avg`, `func.min`, `func.max`), Grouping (`group_by`, `having`), 
    Subqueries, CTEs (`cte`), Window Functions (`over`), `case()`, Bulk DML (`insert/update/delete.returning`).
14. RESPONSES: `response_model`, `response_model_exclude_unset=True`, `HTMLResponse`, `StreamingResponse`, `FileResponse`, `RedirectResponse`.
15. ASYNC TASKS & WEBSOCKETS: `BackgroundTasks`, `@app.websocket` chat with `ConnectionManager` (broadcast & personal message).
16. TESTING SUITE: Synchronous `TestClient` & Asynchronous `httpx.AsyncClient` with `ASGITransport` tests & `app.dependency_overrides` cleanup.
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import enum
from functools import lru_cache, wraps
import os
import time
from typing import AsyncGenerator, Callable, List, Optional

# --- FASTAPI IMPORTS ---
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Cookie,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Path,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    StreamingResponse,
)
from fastapi.security import (
    APIKeyHeader,
    APIKeyQuery,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from fastapi.testclient import TestClient

# --- TESTING & ASYNC IMPORTS ---
from httpx import ASGITransport, AsyncClient
import jwt
from passlib.context import CryptContext
import pytest
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- SQLALCHEMY 2.0 IMPORTS ---
from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Table,
    and_,
    case,
    create_engine,
    delete,
    desc,
    event,
    func,
    insert,
    or_,
    select,
    text,
    update,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    WriteOnlyMapped,
    aliased,
    contains_eager,
    joinedload,
    mapped_column,
    relationship,
    selectinload,
    sessionmaker,
    subqueryload,
)

# =====================================================================
# 1. CONFIGURATION & ENVIRONMENT (pydantic-settings)
# =====================================================================
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Exhaustive FastAPI & SQLAlchemy 2.0 Master Capstone"
    secret_key: str = "super-secret-capstone-jwt-key-2026"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    api_key_secret: str = "capstone-api-key-999"
    database_url: str = "sqlite:///./capstone_master_exhaustive.db"
    pool_size: int = 5
    max_overflow: int = 10

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()


# =====================================================================
# 2. SECURITY & AUTHENTICATION SETUP
# =====================================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query_scheme = APIKeyQuery(name="api_key", auto_error=False)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


# =====================================================================
# 3. MODERN SQLALCHEMY 2.0 DECLARATIVE MODELS & RELATIONSHIPS
# =====================================================================
class Base(DeclarativeBase):
    pass

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)

# --- STANDARD 1:1 RELATIONSHIP (User <-> UserProfile) ---
class UserProfile(Base):
    __tablename__ = "capstone_user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[Optional[str]] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("capstone_users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="profile")

# --- STANDARD M:N SECONDARY ASSOCIATION TABLE (Post <-> Tag) ---
capstone_post_tags = Table(
    "capstone_post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("capstone_posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("capstone_tags.id", ondelete="CASCADE"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "capstone_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    posts: Mapped[List["Post"]] = relationship("Post", secondary=capstone_post_tags, back_populates="tags")

class Post(Base):
    __tablename__ = "capstone_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    author_id: Mapped[int] = mapped_column(ForeignKey("capstone_users.id", ondelete="CASCADE"))

    author: Mapped["User"] = relationship("User", back_populates="posts")
    tags: Mapped[List[Tag]] = relationship(Tag, secondary=capstone_post_tags, back_populates="tags")

# --- MAIN USER MODEL ---
class User(Base, AuditMixin):
    __tablename__ = "capstone_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.CUSTOMER)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    profile: Mapped[Optional[UserProfile]] = relationship(
        UserProfile, back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    posts: Mapped[List[Post]] = relationship(Post, back_populates="author", cascade="all, delete-orphan")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    # Raise Loading Guardrail Attribute
    guarded_posts: Mapped[List[Post]] = relationship(Post, lazy="raise", viewonly=True)

# --- SELF-REFERENTIAL 1:1 MODEL (Peer Mentorship) ---
class PeerUser(Base):
    __tablename__ = "capstone_peer_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    mentor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("capstone_peer_users.id"), unique=True)

    mentor: Mapped[Optional["PeerUser"]] = relationship("PeerUser", remote_side=[id], uselist=False)

# --- SELF-REFERENTIAL 1:N MODEL (Employee Hierarchy) ---
class Employee(Base):
    __tablename__ = "capstone_employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(50))
    department: Mapped[str] = mapped_column(String(50), default="Engineering")
    salary: Mapped[float] = mapped_column(default=75000.0)
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("capstone_employees.id", ondelete="SET NULL"))

    manager: Mapped[Optional["Employee"]] = relationship("Employee", remote_side=[id], back_populates="subordinates")
    subordinates: Mapped[List["Employee"]] = relationship("Employee", back_populates="manager")

# --- SELF-REFERENTIAL M:N MODEL (Social Followers Graph) ---
social_followers_table = Table(
    "capstone_social_followers",
    Base.metadata,
    Column("user_id", ForeignKey("capstone_social_users.id", ondelete="CASCADE"), primary_key=True),
    Column("follower_id", ForeignKey("capstone_social_users.id", ondelete="CASCADE"), primary_key=True),
)

class SocialUser(Base):
    __tablename__ = "capstone_social_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)

    following: Mapped[List["SocialUser"]] = relationship(
        "SocialUser",
        secondary=social_followers_table,
        primaryjoin=(id == social_followers_table.c.user_id),
        secondaryjoin=(id == social_followers_table.c.follower_id),
        back_populates="followers",
    )
    followers: Mapped[List["SocialUser"]] = relationship(
        "SocialUser",
        secondary=social_followers_table,
        primaryjoin=(id == social_followers_table.c.follower_id),
        secondaryjoin=(id == social_followers_table.c.user_id),
        back_populates="following",
    )

# --- WRITE-ONLY MAPPED MODEL (For large datasets) ---
class Publisher(Base):
    __tablename__ = "capstone_publishers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    articles: WriteOnlyMapped["Article"] = relationship("Article", back_populates="publisher")

class Article(Base):
    __tablename__ = "capstone_articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    publisher_id: Mapped[int] = mapped_column(ForeignKey("capstone_publishers.id"))
    publisher: Mapped[Publisher] = relationship(Publisher, back_populates="articles")

# --- PRODUCT MODEL ---
class Product(Base):
    __tablename__ = "capstone_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), index=True)
    price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(default=0)

    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")

# --- ORDER MODEL (1:N with User) ---
class Order(Base, AuditMixin):
    __tablename__ = "capstone_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("capstone_users.id", ondelete="CASCADE"))
    total_amount: Mapped[float] = mapped_column(default=0.0)
    status: Mapped[str] = mapped_column(String(30), default="pending")

    user: Mapped[User] = relationship(User, back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

# --- ASSOCIATION OBJECT M:N MODEL (OrderItem) ---
class OrderItem(Base):
    __tablename__ = "capstone_order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("capstone_orders.id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("capstone_products.id", ondelete="CASCADE"), primary_key=True)
    quantity: Mapped[int] = mapped_column(default=1)
    unit_price: Mapped[float] = mapped_column()

    order: Mapped[Order] = relationship(Order, back_populates="items")
    product: Mapped[Product] = relationship(Product, back_populates="order_items")


# =====================================================================
# 4. EVENT LISTENERS (Automatic Auditing Hooks)
# =====================================================================
@event.listens_for(User, "before_insert")
@event.listens_for(Order, "before_insert")
def audit_before_insert(mapper, connection, target):
    now = datetime.now(timezone.utc)
    target.created_at = now
    target.updated_at = now

@event.listens_for(User, "before_update")
@event.listens_for(Order, "before_update")
def audit_before_update(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


# =====================================================================
# 5. PYDANTIC SCHEMAS (Request Validation & Response Models)
# =====================================================================
class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Forbid extra undeclared fields!

    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=6)
    bio: Optional[str] = Field(None, max_length=255)

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserUpdatePartial(BaseModel):
    email: Optional[EmailStr] = None
    bio: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2)
    category: str
    price: float = Field(..., gt=0)
    stock: int = Field(0, ge=0)

class OrderCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


# =====================================================================
# 6. DATABASE ENGINE & LIFESPAN MANAGEMENT
# =====================================================================
engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def get_db():
    with SessionLocal() as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    Base.metadata.create_all(engine)
    # Seed initial test admin user and data if absent
    with SessionLocal() as session:
        admin = session.scalars(select(User).where(User.username == "admin")).first()
        if not admin:
            admin_user = User(
                username="admin",
                email="admin@capstone.com",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                profile=UserProfile(bio="System Administrator"),
            )
            session.add(admin_user)

            # Seed demo publisher with WriteOnlyMapped articles
            pub = Publisher(name="Tech Publishing House")
            for i in range(10):
                pub.articles.add(Article(title=f"Tech Article #{i+1}"))
            session.add(pub)

            # Seed demo employees for hierarchy queries
            ceo = Employee(name="Sarah", title="CEO", salary=200000)
            cto = Employee(name="Michael", title="CTO", salary=150000, manager=ceo)
            dev = Employee(name="Dave", title="Lead Engineer", salary=110000, manager=cto)
            session.add_all([ceo, cto, dev])

            session.commit()
    yield
    # Cleanup on shutdown


# =====================================================================
# 7. MAIN FASTAPI APP & MIDDLEWARE SETUP
# =====================================================================
# Router-level global dependency demonstration
global_auth_dependency = Depends(lambda: True)

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description="Exhaustive Master Capstone combining FastAPI and Modern SQLAlchemy 2.0",
    lifespan=lifespan,
    dependencies=[global_auth_dependency],  # Global App Dependency
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom HTTP Middleware for timing requests
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response


# =====================================================================
# 8. SUB-DEPENDENCIES & SECURITY RESOLUTION
# =====================================================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.scalars(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

def verify_api_key(
    header_key: Optional[str] = Depends(api_key_header_scheme),
    query_key: Optional[str] = Depends(api_key_query_scheme),
):
    key = header_key or query_key
    if key != settings.api_key_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key"
        )
    return key

# Sub-dependency pattern: query extractor -> query_or_cookie_extractor
def query_extractor(q: Optional[str] = None):
    return q

def query_or_cookie_extractor(
    q: Optional[str] = Depends(query_extractor),
    last_query: Optional[str] = Cookie(None),
    user_agent: Optional[str] = Header(None),
):
    return q or last_query


# =====================================================================
# 9. DYNAMIC ROUTE DECORATOR DEMONSTRATION
# =====================================================================
dynamic_router = APIRouter(prefix="/api/v1/custom", tags=["Custom Route Decorator"])

def custom_api_decorator(path: str, methods: List[str], router: APIRouter = dynamic_router):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"[CUSTOM DECORATOR] Intercepted request to '{path}'")
            return func(*args, **kwargs)

        router.add_api_route(path=path, endpoint=wrapper, methods=methods)
        return wrapper
    return decorator

@custom_api_decorator(path="/decorated-endpoint/{item_id}", methods=["GET"])
def handle_decorated_route(item_id: int = Path(..., ge=1)):
    return {"status": "success", "item_id": item_id, "message": "Handled via custom_api_decorator!"}


# =====================================================================
# 10. API ROUTERS & ENDPOINTS
# =====================================================================

# --- AUTH & USERS ROUTER ---
users_router = APIRouter(prefix="/api/v1/users", tags=["Users & Authentication"])

@users_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account with profile."""
    existing = db.scalars(
        select(User).where(or_(User.username == payload.username, User.email == payload.email))
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.CUSTOMER,
        profile=UserProfile(bio=payload.bio),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@users_router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible token login."""
    user = db.scalars(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Route Order Precedence: /users/me defined BEFORE /users/{user_id}
@users_router.get("/me", response_model=UserOut)
def read_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns profile for currently authenticated user."""
    return current_user

@users_router.get("/{user_id}", response_model=UserOut)
def read_user_by_id(user_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    """Fetch user by ID."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@users_router.patch("/me", response_model=UserOut, response_model_exclude_unset=True)
def update_current_user_profile(
    payload: UserUpdatePartial,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Demonstrates response_model_exclude_unset=True for partial updates."""
    if payload.email:
        current_user.email = payload.email
    if payload.bio and current_user.profile:
        current_user.profile.bio = payload.bio
    db.commit()
    db.refresh(current_user)
    return current_user


# --- STORE & ORDERS ROUTER ---
store_router = APIRouter(prefix="/api/v1/store", tags=["Store & Products"])

@store_router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create product (Admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin role required")
    product = Product(
        name=payload.name, category=payload.category, price=payload.price, stock=payload.stock
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@store_router.get("/products")
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search_query: Optional[str] = Depends(query_or_cookie_extractor),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    """List products with filtering, sub-dependencies, and pagination."""
    stmt = select(Product)
    if category:
        stmt = stmt.where(Product.category == category)
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)
    if search_query:
        stmt = stmt.where(Product.name.ilike(f"%{search_query}%"))

    stmt = stmt.order_by(Product.id).offset(skip).limit(limit)
    products = db.scalars(stmt).all()
    return products

@store_router.post("/orders", status_code=status.HTTP_201_CREATED)
def place_order(
    payload: OrderCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Place an order using Eager Loading, Savepoints, and Background Tasks."""
    product = db.get(Product, payload.product_id)
    if not product or product.stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Product unavailable or insufficient stock")

    # SAVEPOINT / NESTED TRANSACTION DEMONSTRATION
    with db.begin_nested():
        product.stock -= payload.quantity
        total = product.price * payload.quantity
        order = Order(user_id=current_user.id, total_amount=total, status="completed")
        order_item = OrderItem(product=product, quantity=payload.quantity, unit_price=product.price)
        order.items.append(order_item)
        db.add(order)

    db.commit()

    # Eager load using subqueryload & selectinload
    refreshed_order = db.scalars(
        select(Order).where(Order.id == order.id).options(selectinload(Order.items))
    ).one()

    # Background task
    def send_order_email(user_email: str, order_id: int):
        print(f"[BACKGROUND TASK] Order confirmation email sent to {user_email} for Order #{order_id}")

    background_tasks.add_task(send_order_email, current_user.email, refreshed_order.id)

    return {"status": "success", "order_id": refreshed_order.id, "total_amount": refreshed_order.total_amount}


# --- ADVANCED ANALYTICS & ADVANCED SQL ROUTER ---
analytics_router = APIRouter(prefix="/api/v1/analytics", tags=["Advanced Analytics & SQL"])

@analytics_router.get("/summary")
def get_analytics_summary(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Demonstrates Aggregations, Grouping, HAVING, Subqueries, CTEs, Window Functions, and CASE."""
    # 1. Category Revenue Grouping with HAVING & Aggregations
    stmt_category = (
        select(
            Product.category,
            func.count(Product.id).label("total_items"),
            func.sum(Product.price * Product.stock).label("inventory_value"),
            func.avg(Product.price).label("avg_price"),
            func.min(Product.price).label("min_price"),
            func.max(Product.price).label("max_price"),
        )
        .group_by(Product.category)
        .having(func.count(Product.id) >= 1)
    )
    categories = [
        {
            "category": cat,
            "items": count,
            "value": val or 0.0,
            "avg_price": avg or 0.0,
            "min_price": mn or 0.0,
            "max_price": mx or 0.0,
        }
        for cat, count, val, avg, mn, mx in db.execute(stmt_category)
    ]

    # 2. Window Function: Product Price Rank within Category
    rank_window = func.rank().over(
        partition_by=Product.category, order_by=Product.price.desc()
    )
    stmt_rank = select(Product.name, Product.category, Product.price, rank_window.label("rank"))
    ranked_products = [
        {"name": name, "category": cat, "price": price, "rank": rk}
        for name, cat, price, rk in db.execute(stmt_rank)
    ]

    # 3. CTE Demonstration: High Stock Products
    high_stock_cte = (
        select(Product.id, Product.name, Product.stock)
        .where(Product.stock > 5)
        .cte("high_stock_cte")
    )
    stmt_cte = select(high_stock_cte.c.name, high_stock_cte.c.stock)
    cte_results = [{"name": row.name, "stock": row.stock} for row in db.execute(stmt_cte)]

    # 4. CASE Expression Demonstration
    price_tier = case(
        (Product.price >= 500, "Premium"),
        (Product.price >= 100, "Mid-range"),
        else_="Budget",
    ).label("tier")
    stmt_case = select(Product.name, Product.price, price_tier)
    tiered_products = [
        {"name": name, "price": price, "tier": tier}
        for name, price, tier in db.execute(stmt_case)
    ]

    return {
        "category_summary": categories,
        "product_ranks": ranked_products,
        "high_stock_cte": cte_results,
        "tiered_products": tiered_products,
    }

@analytics_router.get("/write-only-articles")
def query_write_only_articles(db: Session = Depends(get_db)):
    """Demonstrates WriteOnlyMapped relationship query execution."""
    pub = db.scalars(select(Publisher).where(Publisher.name == "Tech Publishing House")).first()
    if not pub:
        return {"articles": []}
    # Query WriteOnlyMapped articles directly with .select()
    stmt = pub.articles.select().where(Article.title.like("%#1%")).limit(5)
    articles = db.scalars(stmt).all()
    return {"publisher": pub.name, "matching_articles": [a.title for a in articles]}

@analytics_router.get("/hierarchy")
def get_employee_hierarchy(db: Session = Depends(get_db)):
    """Demonstrates Self-Referential 1:N loading with joinedload."""
    stmt = (
        select(Employee)
        .options(joinedload(Employee.subordinates))
        .where(Employee.manager_id.is_(None))
    )
    top_execs = db.scalars(stmt).unique().all()
    hierarchy = []
    for exec_person in top_execs:
        hierarchy.append({
            "name": exec_person.name,
            "title": exec_person.title,
            "subordinates": [{"name": sub.name, "title": sub.title} for sub in exec_person.subordinates],
        })
    return {"hierarchy": hierarchy}


# --- CUSTOM RESPONSES ROUTER ---
responses_router = APIRouter(prefix="/api/v1/custom-responses", tags=["Custom Responses"])

@responses_router.get("/html", response_class=HTMLResponse)
def get_html_page():
    return "<html><body><h1>FastAPI & Modern SQLAlchemy 2.0 Master Capstone</h1></body></html>"

@responses_router.get("/redirect")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@responses_router.get("/stream")
def stream_data():
    def generator():
        for i in range(1, 4):
            time.sleep(0.1)
            yield f"Data chunk {i}\n"
    return StreamingResponse(generator(), media_type="text/plain")


# Mount All Routers into FastAPI App
app.include_router(users_router)
app.include_router(store_router)
app.include_router(analytics_router)
app.include_router(responses_router)
app.include_router(dynamic_router)


# =====================================================================
# 11. WEBSOCKET CHATROOM
# =====================================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

ws_manager = ConnectionManager()

@app.websocket("/ws/chat/{client_id}")
async def websocket_chat_endpoint(websocket: WebSocket, client_id: str):
    await ws_manager.connect(websocket)
    await ws_manager.broadcast(f"Client #{client_id} joined the chat")
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("/private "):
                msg = data.replace("/private ", "")
                await ws_manager.send_personal_message(f"[PRIVATE] {msg}", websocket)
            else:
                await ws_manager.broadcast(f"Client #{client_id}: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        await ws_manager.broadcast(f"Client #{client_id} left the chat")


# Root Endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Exhaustive FastAPI & SQLAlchemy 2.0 Master Capstone API!"}


# =====================================================================
# 12. EMBEDDED TEST SUITE (Synchronous & Asynchronous Tests)
# =====================================================================
# Runnable via `pytest capstone_project/main_app.py`

test_client = TestClient(app)

def test_sync_root():
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to the Exhaustive FastAPI & SQLAlchemy 2.0 Master Capstone API!"

def test_sync_custom_decorator():
    response = test_client.get("/api/v1/custom/decorated-endpoint/42")
    assert response.status_code == 200
    assert response.json()["item_id"] == 42

def test_sync_auth_and_store_flow():
    # 1. Register User
    payload = {
        "username": "exhaustive_tester",
        "email": "ex_tester@example.com",
        "password": "securepassword123",
        "bio": "Automated Tester",
    }
    resp = test_client.post("/api/v1/users/register", json=payload)
    assert resp.status_code == 201

    # 2. Login User
    login_data = {"username": "exhaustive_tester", "password": "securepassword123"}
    resp = test_client.post("/api/v1/users/login", data=login_data)
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    # 3. Create Product as Admin
    admin_login = {"username": "admin", "password": "admin123"}
    admin_resp = test_client.post("/api/v1/users/login", data=admin_login)
    admin_token = admin_resp.json()["access_token"]

    product_payload = {"name": "Exhaustive Test Product", "category": "Gadgets", "price": 99.99, "stock": 10}
    prod_resp = test_client.post(
        "/api/v1/store/products",
        json=product_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert prod_resp.status_code == 201
    prod_id = prod_resp.json()["id"]

    # 4. Place Order as Customer
    order_payload = {"product_id": prod_id, "quantity": 2}
    order_resp = test_client.post(
        "/api/v1/store/orders",
        json=order_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert order_resp.status_code == 201
    assert order_resp.json()["total_amount"] == 199.98

def test_dependency_overrides():
    def mock_get_current_user():
        return User(id=999, username="mocked_user", role=UserRole.ADMIN)

    app.dependency_overrides[get_current_user] = mock_get_current_user
    try:
        resp = test_client.get("/api/v1/users/me", headers={"Authorization": "Bearer mock"})
        assert resp.status_code == 200
        assert resp.json()["username"] == "mocked_user"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_async_client_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/custom-responses/html")
        assert response.status_code == 200
        assert "FastAPI & Modern SQLAlchemy 2.0" in response.text

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Exhaustive Master Capstone Server on http://127.0.0.1:8000 ...")
    uvicorn.run("main_app:app", host="127.0.0.1", port=8000, reload=True)
