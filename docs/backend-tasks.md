# Backend Implementation Tasks - Детальная декомпозиция

## Обзор
150+ атомарных задач для реализации FastAPI backend с полной функциональностью.
Каждая задача включает код-сниппеты, структуру файлов и тестовые сценарии.

---

## СЕКЦИЯ 1: Инициализация проекта (10 задач)

### BE-001: Создать структуру проекта
**Время**: 30 мин
**Файлы для создания**:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── db/
│       └── __init__.py
├── tests/
├── alembic/
├── requirements.txt
├── .env.example
└── pyproject.toml
```

**Код для main.py**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FitCoach API",
    description="Personal health and habits tracker",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FitCoach API v1.0.0"}
```

### BE-002: Настроить Poetry
**Время**: 30 мин
**Файл pyproject.toml**:
```toml
[tool.poetry]
name = "fitcoach-backend"
version = "0.1.0"
description = "FitCoach Backend API"
authors = ["Your Name"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
sqlalchemy = "^2.0.23"
alembic = "^1.12.0"
psycopg2-binary = "^2.9.9"
pydantic = "^2.4.2"
pydantic-settings = "^2.0.3"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
email-validator = "^2.1.0"
redis = "^5.0.1"
langchain = "^0.1.0"
openai = "^1.0.0"
httpx = "^0.25.0"
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
black = "^23.11.0"
isort = "^5.12.0"
flake8 = "^6.1.0"
mypy = "^1.7.0"
pre-commit = "^3.5.0"
```

**Команды**:
```bash
poetry install
poetry shell
```

### BE-003: Создать конфигурацию
**Время**: 1ч
**Файл app/core/config.py**:
```python
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets

class Settings(BaseSettings):
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FitCoach"
    VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode='before')
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # First superuser
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings = Settings()
```

### BE-004: Настроить подключение к БД
**Время**: 1ч
**Файл app/db/base.py**:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### BE-005: Настроить Alembic
**Время**: 1ч
**Команды**:
```bash
alembic init alembic
```

**Файл alembic.ini (изменения)**:
```ini
sqlalchemy.url = postgresql://user:pass@localhost/dbname
```

**Файл alembic/env.py**:
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.db.base import Base
from app.core.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## СЕКЦИЯ 2: Модели данных (25 задач)

### BE-011: Модель User
**Время**: 1ч
**Файл app/models/user.py**:
```python
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)

    # Profile fields
    age = Column(Integer)
    height = Column(Float)  # in cm
    weight = Column(Float)  # in kg
    target_weight = Column(Float)

    # Settings
    language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    water_goal = Column(Float, default=2.5)  # liters
    calorie_goal = Column(Integer, default=2000)
    sleep_goal = Column(Float, default=8.0)  # hours

    # Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    days = relationship("Day", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
```

### BE-012: Модель Day
**Время**: 1ч
**Файл app/models/day.py**:
```python
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Day(Base):
    __tablename__ = "days"
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='_user_date_uc'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Main metrics
    tag = Column(String)  # Custom tag for the day
    feeling = Column(Integer)  # 1-5 scale
    effort_score = Column(Float)  # 0-10 from LLM

    # Summary
    summary = Column(Text)
    llm_advice = Column(Text)

    # Relationships
    user = relationship("User", back_populates="days")
    meals = relationship("Meal", back_populates="day", cascade="all, delete-orphan")
    exercises = relationship("Exercise", back_populates="day", cascade="all, delete-orphan")
    water_intakes = relationship("WaterIntake", back_populates="day", cascade="all, delete-orphan")
    sleep_records = relationship("Sleep", back_populates="day", cascade="all, delete-orphan")
    mood_records = relationship("Mood", back_populates="day", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="day", cascade="all, delete-orphan")

    # Computed properties
    @property
    def total_calories(self):
        return sum(meal.calories for meal in self.meals if meal.calories)

    @property
    def total_water(self):
        return sum(intake.amount for intake in self.water_intakes)

    @property
    def total_exercise_minutes(self):
        return sum(ex.duration for ex in self.exercises if ex.duration)
```

### BE-013: Модель Meal
**Время**: 1ч
**Файл app/models/meal.py**:
```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("days.id"), nullable=False)

    category = Column(String, nullable=False)  # breakfast, lunch, dinner, snack
    time = Column(DateTime(timezone=True))

    # Nutrition
    calories = Column(Float)
    protein = Column(Float)  # grams
    carbs = Column(Float)    # grams
    fat = Column(Float)      # grams
    fiber = Column(Float)    # grams
    sugar = Column(Float)    # grams
    sodium = Column(Float)   # mg

    # Details
    items = Column(JSON)  # List of food items
    notes = Column(Text)
    photo_url = Column(String)

    # AI
    ai_summary = Column(Text)
    ai_suggestions = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    day = relationship("Day", back_populates="meals")

class MealItem(Base):
    __tablename__ = "meal_items"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)

    name = Column(String, nullable=False)
    amount = Column(Float)
    unit = Column(String)  # g, ml, cup, piece, etc
    calories = Column(Float)

    meal = relationship("Meal", backref="meal_items")
```

### BE-014: Модель Exercise
**Время**: 1ч
**Файл app/models/exercise.py**:
```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("days.id"), nullable=False)

    type = Column(String, nullable=False)  # running, gym, yoga, cycling, etc
    name = Column(String)  # Specific exercise name

    # Time & Duration
    start_time = Column(DateTime(timezone=True))
    duration = Column(Integer)  # minutes

    # Metrics
    distance = Column(Float)  # km
    calories_burned = Column(Float)
    heart_rate_avg = Column(Integer)
    heart_rate_max = Column(Integer)

    # Intensity
    intensity = Column(Integer)  # 1-5 scale

    # Details
    sets_reps = Column(JSON)  # For gym: [{exercise, sets, reps, weight}]
    route = Column(JSON)  # For running: GPS coordinates
    notes = Column(Text)

    # AI
    ai_feedback = Column(Text)
    ai_recommendations = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    day = relationship("Day", back_populates="exercises")

class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)

    set_number = Column(Integer)
    reps = Column(Integer)
    weight = Column(Float)  # kg
    rest_seconds = Column(Integer)

    exercise = relationship("Exercise", backref="sets")
```

### BE-015: Модель Water, Sleep, Mood
**Время**: 1.5ч
**Файл app/models/tracking.py**:
```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class WaterIntake(Base):
    __tablename__ = "water_intakes"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("days.id"), nullable=False)

    amount = Column(Float, nullable=False)  # liters
    time = Column(DateTime(timezone=True), server_default=func.now())

    day = relationship("Day", back_populates="water_intakes")

class Sleep(Base):
    __tablename__ = "sleep_records"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("days.id"), nullable=False)

    bedtime = Column(DateTime(timezone=True))
    wake_time = Column(DateTime(timezone=True))
    duration = Column(Float)  # hours (calculated)

    quality = Column(Integer)  # 1-5 scale
    deep_sleep = Column(Float)  # hours
    rem_sleep = Column(Float)   # hours

    interruptions = Column(Integer)
    notes = Column(Text)

    # AI Analysis
    ai_analysis = Column(Text)
    ai_recommendations = Column(Text)

    day = relationship("Day", back_populates="sleep_records")

class Mood(Base):
    __tablename__ = "mood_records"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("days.id"), nullable=False)

    time = Column(DateTime(timezone=True), server_default=func.now())
    rating = Column(Integer, nullable=False)  # 1-5 scale

    # Mood tags
    energy_level = Column(Integer)  # 1-5
    stress_level = Column(Integer)  # 1-5
    anxiety_level = Column(Integer)  # 1-5

    tags = Column(JSON)  # ["happy", "tired", "stressed", "focused", etc]

    notes = Column(Text)

    # AI Analysis
    ai_sentiment = Column(String)
    ai_suggestions = Column(Text)

    day = relationship("Day", back_populates="mood_records")
```

### BE-016: Модель Note и LLMSummary
**Время**: 1ч
**Файл app/models/content.py**:
```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("days.id"), nullable=False)

    title = Column(String)
    content = Column(Text, nullable=False)  # Markdown

    tags = Column(JSON)
    attachments = Column(JSON)  # URLs to files

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    day = relationship("Day", back_populates="notes")

class LLMSummary(Base):
    __tablename__ = "llm_summaries"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("days.id"), nullable=False, unique=True)

    # Main summary
    summary_text = Column(Text, nullable=False)
    effort_score = Column(Float, nullable=False)  # 0-10
    score_reason = Column(Text)

    # Detailed analysis
    nutrition_analysis = Column(Text)
    exercise_analysis = Column(Text)
    sleep_analysis = Column(Text)
    mood_analysis = Column(Text)

    # Recommendations
    tomorrow_advice = Column(Text)
    weekly_goals = Column(JSON)

    # Meta
    model_used = Column(String)
    prompt_version = Column(String)
    tokens_used = Column(Integer)
    generation_time = Column(Float)  # seconds

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    day = relationship("Day", backref="llm_summary", uselist=False)
```

---

## СЕКЦИЯ 3: Schemas/Pydantic (20 задач)

### BE-036: User Schemas
**Время**: 1ч
**Файл app/schemas/user.py**:
```python
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=150)
    height: Optional[float] = Field(None, ge=50, le=300)
    weight: Optional[float] = Field(None, ge=20, le=500)
    target_weight: Optional[float] = Field(None, ge=20, le=500)

class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    target_weight: Optional[float] = None

    # Settings
    language: Optional[str] = None
    timezone: Optional[str] = None
    water_goal: Optional[float] = None
    calorie_goal: Optional[int] = None
    sleep_goal: Optional[float] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserInDB):
    pass

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
```

### BE-037: Day Schemas
**Время**: 1ч
**Файл app/schemas/day.py**:
```python
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.meal import MealResponse
from app.schemas.exercise import ExerciseResponse
from app.schemas.tracking import WaterIntakeResponse, SleepResponse, MoodResponse
from app.schemas.content import NoteResponse, LLMSummaryResponse

class DayBase(BaseModel):
    date: date
    tag: Optional[str] = None
    feeling: Optional[int] = Field(None, ge=1, le=5)

class DayCreate(DayBase):
    pass

class DayUpdate(BaseModel):
    tag: Optional[str] = None
    feeling: Optional[int] = Field(None, ge=1, le=5)
    summary: Optional[str] = None

class DayInDB(DayBase):
    id: int
    user_id: int
    effort_score: Optional[float] = None
    summary: Optional[str] = None
    llm_advice: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DayResponse(DayInDB):
    # Computed fields
    total_calories: Optional[float] = None
    total_water: Optional[float] = None
    total_exercise_minutes: Optional[int] = None

    # Related data (optional, based on query params)
    meals: Optional[List[MealResponse]] = []
    exercises: Optional[List[ExerciseResponse]] = []
    water_intakes: Optional[List[WaterIntakeResponse]] = []
    sleep_records: Optional[List[SleepResponse]] = []
    mood_records: Optional[List[MoodResponse]] = []
    notes: Optional[List[NoteResponse]] = []
    llm_summary: Optional[LLMSummaryResponse] = None

class DayListResponse(BaseModel):
    days: List[DayResponse]
    total: int
    page: int
    per_page: int
```

### BE-038: Meal Schemas
**Время**: 1ч
**Файл app/schemas/meal.py**:
```python
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class MealItemBase(BaseModel):
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    calories: Optional[float] = None

class MealBase(BaseModel):
    category: str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$")
    time: Optional[datetime] = None
    calories: Optional[float] = Field(None, ge=0)
    protein: Optional[float] = Field(None, ge=0)
    carbs: Optional[float] = Field(None, ge=0)
    fat: Optional[float] = Field(None, ge=0)
    fiber: Optional[float] = Field(None, ge=0)
    sugar: Optional[float] = Field(None, ge=0)
    sodium: Optional[float] = Field(None, ge=0)
    items: Optional[List[MealItemBase]] = []
    notes: Optional[str] = None

class MealCreate(MealBase):
    pass

class MealUpdate(MealBase):
    category: Optional[str] = None

class MealInDB(MealBase):
    id: int
    day_id: int
    created_at: datetime
    photo_url: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_suggestions: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class MealResponse(MealInDB):
    pass

class NutritionSummary(BaseModel):
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    meals_count: int
    average_calories_per_meal: float
```

---

## СЕКЦИЯ 4: Auth и Security (15 задач)

### BE-056: Password Hashing
**Время**: 1ч
**Файл app/core/security.py**:
```python
from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(
    subject: Union[str, Any],
    expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### BE-057: JWT Dependencies
**Время**: 1ч
**Файл app/api/deps.py**:
```python
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app import models, schemas
from app.core import security
from app.core.config import settings
from app.db.base import get_db

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception

    except (JWTError, ValidationError):
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user

def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions"
        )
    return current_user
```

### BE-058: Auth Endpoints
**Время**: 1.5ч
**Файл app/api/v1/endpoints/auth.py**:
```python
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.services import user as user_service

router = APIRouter()

@router.post("/login", response_model=schemas.TokenResponse)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login"""
    user = user_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)

    # Save refresh token
    user_service.save_refresh_token(db, user.id, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=schemas.UserResponse)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate
) -> Any:
    """Create new user"""
    user = db.query(models.User).filter(
        models.User.email == user_in.email
    ).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    user = user_service.create_user(db, user_in)

    # Send verification email (async task)
    # background_tasks.add_task(
    #     send_verification_email, user.email, user.id
    # )

    return user

@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh_token(
    *,
    db: Session = Depends(deps.get_db),
    refresh_token: str = Body(..., embed=True)
) -> Any:
    """Refresh access token"""
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if not user_id or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Verify refresh token in DB
    if not user_service.verify_refresh_token(db, user_id, refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or expired"
        )

    # Generate new tokens
    access_token = security.create_access_token(user_id)
    new_refresh_token = security.create_refresh_token(user_id)

    # Update refresh token
    user_service.update_refresh_token(
        db, user_id, refresh_token, new_refresh_token
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    refresh_token: str = Body(..., embed=True)
) -> Any:
    """Logout and invalidate refresh token"""
    user_service.delete_refresh_token(db, current_user.id, refresh_token)
    return {"message": "Successfully logged out"}
```

---

## СЕКЦИЯ 5: CRUD Services (30 задач)

### BE-071: User Service
**Время**: 1.5ч
**Файл app/services/user.py**:
```python
from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.models import User, RefreshToken
from app.schemas import UserCreate, UserUpdate
from datetime import datetime, timedelta

class UserService:
    def get(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def create(self, db: Session, user_in: UserCreate) -> User:
        user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            age=user_in.age,
            height=user_in.height,
            weight=user_in.weight,
            target_weight=user_in.target_weight
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(
        self, db: Session, user: User, user_update: UserUpdate
    ) -> User:
        update_data = user_update.dict(exclude_unset=True)

        for field in update_data:
            setattr(user, field, update_data[field])

        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate(
        self, db: Session, email: str, password: str
    ) -> Optional[User]:
        user = self.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()

        return user

    def delete(self, db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

    def save_refresh_token(
        self, db: Session, user_id: int, token: str
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(refresh_token)
        db.commit()
        return refresh_token

user_service = UserService()
```

### BE-072: Day Service
**Время**: 1.5ч
**Файл app/services/day.py**:
```python
from typing import Optional, List
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Day, User
from app.schemas import DayCreate, DayUpdate

class DayService:
    def get(self, db: Session, day_id: int, user_id: int) -> Optional[Day]:
        return db.query(Day).filter(
            and_(Day.id == day_id, Day.user_id == user_id)
        ).first()

    def get_by_date(
        self, db: Session, user_id: int, date: date
    ) -> Optional[Day]:
        return db.query(Day).filter(
            and_(Day.user_id == user_id, Day.date == date)
        ).first()

    def get_multi(
        self,
        db: Session,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Day]:
        query = db.query(Day).filter(Day.user_id == user_id)

        if start_date:
            query = query.filter(Day.date >= start_date)
        if end_date:
            query = query.filter(Day.date <= end_date)

        return query.order_by(Day.date.desc()).offset(skip).limit(limit).all()

    def create(
        self, db: Session, user_id: int, day_in: DayCreate
    ) -> Day:
        # Check if day already exists
        existing = self.get_by_date(db, user_id, day_in.date)
        if existing:
            raise ValueError(f"Day {day_in.date} already exists")

        day = Day(
            user_id=user_id,
            date=day_in.date,
            tag=day_in.tag,
            feeling=day_in.feeling
        )
        db.add(day)
        db.commit()
        db.refresh(day)
        return day

    def update(
        self, db: Session, day: Day, day_update: DayUpdate
    ) -> Day:
        update_data = day_update.dict(exclude_unset=True)

        for field in update_data:
            setattr(day, field, update_data[field])

        db.add(day)
        db.commit()
        db.refresh(day)
        return day

    def delete(self, db: Session, day_id: int, user_id: int) -> bool:
        day = self.get(db, day_id, user_id)
        if day:
            db.delete(day)
            db.commit()
            return True
        return False

    def copy_day(
        self, db: Session, user_id: int, from_date: date, to_date: date
    ) -> Day:
        """Copy all data from one day to another"""
        source_day = self.get_by_date(db, user_id, from_date)
        if not source_day:
            raise ValueError(f"Source day {from_date} not found")

        # Check target doesn't exist
        if self.get_by_date(db, user_id, to_date):
            raise ValueError(f"Target day {to_date} already exists")

        # Create new day with copied data
        new_day = Day(
            user_id=user_id,
            date=to_date,
            tag=source_day.tag,
            feeling=source_day.feeling
        )
        db.add(new_day)
        db.flush()

        # Copy related data
        for meal in source_day.meals:
            new_meal = Meal(
                day_id=new_day.id,
                category=meal.category,
                calories=meal.calories,
                protein=meal.protein,
                carbs=meal.carbs,
                fat=meal.fat,
                items=meal.items,
                notes=meal.notes
            )
            db.add(new_meal)

        # Copy exercises, water, sleep, etc...

        db.commit()
        db.refresh(new_day)
        return new_day

day_service = DayService()
```

---

## СЕКЦИЯ 6: API Endpoints детализация (50 задач)

### BE-101-110: Days API
**Время**: 5ч
**Файл app/api/v1/endpoints/days.py**:
```python
from typing import Any, List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.services import day as day_service

router = APIRouter()

@router.get("/", response_model=schemas.DayListResponse)
def get_days(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    include_details: bool = Query(False)
) -> Any:
    """Get list of days for current user"""
    days = day_service.get_multi(
        db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

    # Optionally load related data
    if include_details:
        for day in days:
            db.refresh(day, ['meals', 'exercises', 'water_intakes'])

    total = db.query(models.Day).filter(
        models.Day.user_id == current_user.id
    ).count()

    return {
        "days": days,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit
    }

@router.get("/{date}", response_model=schemas.DayResponse)
def get_day(
    date: date,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    include_meals: bool = Query(True),
    include_exercises: bool = Query(True),
    include_water: bool = Query(True),
    include_sleep: bool = Query(True),
    include_mood: bool = Query(True),
    include_notes: bool = Query(True),
    include_summary: bool = Query(True)
) -> Any:
    """Get specific day by date"""
    day = day_service.get_by_date(db, current_user.id, date)

    if not day:
        raise HTTPException(
            status_code=404,
            detail=f"Day {date} not found"
        )

    # Lazy load requested relations
    response = schemas.DayResponse.from_orm(day)

    if include_meals:
        response.meals = day.meals
    if include_exercises:
        response.exercises = day.exercises
    if include_water:
        response.water_intakes = day.water_intakes
    if include_sleep:
        response.sleep_records = day.sleep_records
    if include_mood:
        response.mood_records = day.mood_records
    if include_notes:
        response.notes = day.notes
    if include_summary and day.llm_summary:
        response.llm_summary = day.llm_summary

    # Calculate computed fields
    response.total_calories = day.total_calories
    response.total_water = day.total_water
    response.total_exercise_minutes = day.total_exercise_minutes

    return response

@router.post("/", response_model=schemas.DayResponse)
def create_day(
    *,
    db: Session = Depends(deps.get_db),
    day_in: schemas.DayCreate,
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Create new day"""
    try:
        day = day_service.create(db, current_user.id, day_in)
        return day
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{date}", response_model=schemas.DayResponse)
def update_day(
    date: date,
    *,
    db: Session = Depends(deps.get_db),
    day_update: schemas.DayUpdate,
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Update day"""
    day = day_service.get_by_date(db, current_user.id, date)

    if not day:
        raise HTTPException(status_code=404, detail="Day not found")

    day = day_service.update(db, day, day_update)
    return day

@router.delete("/{date}")
def delete_day(
    date: date,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Delete day and all related data"""
    day = day_service.get_by_date(db, current_user.id, date)

    if not day:
        raise HTTPException(status_code=404, detail="Day not found")

    day_service.delete(db, day.id, current_user.id)
    return {"message": f"Day {date} deleted"}

@router.post("/{date}/copy")
def copy_day(
    date: date,
    target_date: date = Query(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Copy all day data to another date"""
    try:
        new_day = day_service.copy_day(
            db, current_user.id, date, target_date
        )
        return new_day
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## СЕКЦИЯ 7: LLM Integration детализация (15 задач)

### LLM-001: LangChain Setup
**Время**: 2ч
**Файл app/services/llm/base.py**:
```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StdOutCallbackHandler
from app.core.config import settings
import json

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL,
            temperature=0.7,
            max_tokens=1000
        )

        self.memory = ConversationBufferMemory(
            return_messages=True
        )

        self.callbacks = [StdOutCallbackHandler()]

    def create_daily_summary_chain(self):
        system_template = """You are FitCoach AI, a supportive health and wellness assistant.
        Your role is to analyze daily health data and provide constructive, motivating feedback.

        Guidelines:
        - Be encouraging but honest
        - Focus on progress, not perfection
        - Provide actionable advice
        - Keep responses concise (4-6 sentences for summary)
        - Use a warm, supportive tone
        - Never provide medical diagnosis
        """

        human_template = """Please analyze this day's health data and provide:
        1. A daily summary (4-6 sentences)
        2. An effort score (0-10)
        3. Brief reason for the score
        4. One specific micro-step for tomorrow

        Day Data:
        Date: {date}
        Feeling: {feeling}/5

        Nutrition:
        - Total calories: {calories}
        - Meals: {meals_count}
        - Water intake: {water_liters}L

        Exercise:
        - Total minutes: {exercise_minutes}
        - Types: {exercise_types}

        Sleep:
        - Duration: {sleep_hours} hours
        - Quality: {sleep_quality}/5

        Mood:
        - Average rating: {mood_rating}/5
        - Tags: {mood_tags}

        Notes: {user_notes}

        User Goals:
        - Water goal: {water_goal}L
        - Calorie goal: {calorie_goal}
        - Sleep goal: {sleep_goal} hours

        Please format your response as JSON:
        {{
            "summary": "...",
            "effort_score": 0-10,
            "score_reason": "...",
            "tomorrow_advice": "..."
        }}"""

        system_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages([
            system_prompt,
            human_prompt
        ])

        return LLMChain(
            llm=self.llm,
            prompt=chat_prompt,
            callbacks=self.callbacks
        )

    def generate_daily_summary(self, day_data: dict) -> dict:
        chain = self.create_daily_summary_chain()

        result = chain.run(
            date=day_data.get("date"),
            feeling=day_data.get("feeling", "N/A"),
            calories=day_data.get("total_calories", 0),
            meals_count=day_data.get("meals_count", 0),
            water_liters=day_data.get("water_liters", 0),
            exercise_minutes=day_data.get("exercise_minutes", 0),
            exercise_types=", ".join(day_data.get("exercise_types", [])),
            sleep_hours=day_data.get("sleep_hours", 0),
            sleep_quality=day_data.get("sleep_quality", "N/A"),
            mood_rating=day_data.get("mood_rating", "N/A"),
            mood_tags=", ".join(day_data.get("mood_tags", [])),
            user_notes=day_data.get("notes", ""),
            water_goal=day_data.get("water_goal", 2.5),
            calorie_goal=day_data.get("calorie_goal", 2000),
            sleep_goal=day_data.get("sleep_goal", 8)
        )

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # Fallback parsing
            return {
                "summary": result,
                "effort_score": 5.0,
                "score_reason": "Unable to parse score",
                "tomorrow_advice": "Keep going!"
            }

llm_service = LLMService()
```

### LLM-002: Summary Endpoint
**Время**: 1ч
**Файл app/api/v1/endpoints/llm.py**:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.services.llm import llm_service
from app.services import day as day_service
import asyncio

router = APIRouter()

@router.post("/days/{date}/summary")
async def generate_summary(
    date: date,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    regenerate: bool = False
) -> Any:
    """Generate AI summary for a day"""

    day = day_service.get_by_date(db, current_user.id, date)
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")

    # Check if summary exists and not regenerating
    if day.llm_summary and not regenerate:
        return day.llm_summary

    # Prepare data for LLM
    day_data = {
        "date": str(day.date),
        "feeling": day.feeling,
        "total_calories": sum(m.calories or 0 for m in day.meals),
        "meals_count": len(day.meals),
        "water_liters": sum(w.amount for w in day.water_intakes),
        "exercise_minutes": sum(e.duration or 0 for e in day.exercises),
        "exercise_types": list(set(e.type for e in day.exercises)),
        "sleep_hours": day.sleep_records[0].duration if day.sleep_records else 0,
        "sleep_quality": day.sleep_records[0].quality if day.sleep_records else None,
        "mood_rating": sum(m.rating for m in day.mood_records) / len(day.mood_records) if day.mood_records else None,
        "mood_tags": [tag for m in day.mood_records for tag in (m.tags or [])],
        "notes": "\n".join(n.content for n in day.notes),
        "water_goal": current_user.water_goal,
        "calorie_goal": current_user.calorie_goal,
        "sleep_goal": current_user.sleep_goal
    }

    # Generate summary
    try:
        result = await asyncio.to_thread(
            llm_service.generate_daily_summary,
            day_data
        )

        # Save to database
        if day.llm_summary:
            summary = day.llm_summary
        else:
            summary = models.LLMSummary(day_id=day.id)

        summary.summary_text = result["summary"]
        summary.effort_score = result["effort_score"]
        summary.score_reason = result["score_reason"]
        summary.tomorrow_advice = result["tomorrow_advice"]
        summary.model_used = settings.OPENAI_MODEL

        db.add(summary)
        db.commit()
        db.refresh(summary)

        return summary

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )
```

---

## СЕКЦИЯ 8: Testing (20 задач)

### TEST-001: Test Configuration
**Время**: 1ч
**Файл tests/conftest.py**:
```python
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base, get_db
from app.core.config import settings
from app.models import User
from app.core.security import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "postgresql://test:test@localhost/fitcoach_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db) -> Generator:
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user(db) -> User:
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### TEST-002: Auth Tests
**Время**: 1ч
**Файл tests/test_auth.py**:
```python
import pytest
from fastapi.testclient import TestClient

def test_register(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": "newpass123",
            "full_name": "New User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data

def test_login(client: TestClient, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401

def test_refresh_token(client: TestClient, test_user):
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpass123"}
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_current_user(client: TestClient, auth_headers):
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
```

---

## Итоговые метрики Backend

- **Количество файлов**: 50+
- **Строк кода**: ~5000
- **Тестовое покрытие**: 80%+
- **API endpoints**: 50+
- **Модели данных**: 15
- **Сервисы**: 10
- **Время реализации**: ~150 часов

Каждая задача включает:
1. Точные пути файлов
2. Полный код или его ключевые части
3. Конфигурацию и зависимости
4. Примеры использования
5. Тестовые сценарии