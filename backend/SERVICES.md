# FitCoach Backend - Services Documentation

**Status**: ✅ MVP Complete (Core services implemented)
**Framework**: FastAPI + SQLAlchemy 2.0 + Pydantic

This document provides comprehensive documentation for all service layer components in the FitCoach backend API.

---

## 📁 Architecture Overview

FitCoach backend follows a layered architecture pattern:

```
┌─────────────────────────────────────┐
│      API Endpoints (FastAPI)        │  ← HTTP Request/Response
├─────────────────────────────────────┤
│    Schemas (Pydantic Validation)    │  ← Data validation & serialization
├─────────────────────────────────────┤
│     Services (Business Logic)       │  ← This document
├─────────────────────────────────────┤
│      Models (SQLAlchemy ORM)        │  ← Database entities
├─────────────────────────────────────┤
│      Database (PostgreSQL)          │  ← Persistent storage
└─────────────────────────────────────┘
```

### Service Layer Responsibilities

The service layer encapsulates business logic and handles:
- **Data validation**: Beyond schema validation (business rules)
- **Data transformations**: Between models and schemas
- **Database operations**: CRUD through SQLAlchemy
- **Authorization**: User ownership verification
- **Complex queries**: Joins, aggregations, filtering
- **Transaction management**: Ensuring data consistency

---

## 🗂️ Service Files Structure

Located in: `backend/app/services/`

| Service File | Handles | Status | Tests |
|--------------|---------|--------|-------|
| `auth_service.py` | Authentication, JWT, password hashing | ✅ Complete | ✅ 3/3 |
| `user_service.py` | User CRUD operations | ✅ Complete | ✅ 2/2 |
| `day_service.py` | Day entities, nested data | ✅ Complete | ✅ 5/5 |
| `meal_service.py` | Meal tracking | ✅ Complete | ✅ 3/3 |
| `exercise_service.py` | Exercise tracking | ✅ Complete | ✅ 3/3 |
| `water_service.py` | Water intake tracking | ✅ Complete | ✅ 2/2 |
| `sleep_service.py` | Sleep tracking | ⏳ Placeholder | ⏳ 0/0 |
| `mood_service.py` | Mood tracking | ⏳ Placeholder | ⏳ 0/0 |
| `note_service.py` | Notes/journal | ⏳ Placeholder | ⏳ 0/0 |
| `goal_service.py` | Health goals | ⏳ Placeholder | ⏳ 0/0 |
| `llm_service.py` | AI summaries & insights | 📋 Planned | ⏳ 0/0 |
| `notification_service.py` | Push notifications | 📋 Planned | ⏳ 0/0 |

**Total**: 12 services (6 implemented, 3 placeholders, 3 planned)

---

## 🔐 Authentication Service

**File**: `app/services/auth_service.py`
**Status**: ✅ Complete
**Tests**: ✅ 3/3 passing

### Purpose
Handles user authentication, JWT token management, and password security.

### Key Functions

#### `authenticate_user(db, email, password)`
Verifies user credentials and returns user object if valid.

**Parameters**:
- `db: Session` - Database session
- `email: str` - User email
- `password: str` - Plain text password

**Returns**: `User | None` - User object if credentials valid, None otherwise

**Logic**:
1. Query user by email
2. Verify password using bcrypt
3. Return user or None

**Usage**:
```python
user = authenticate_user(db, "user@example.com", "password123")
if not user:
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

---

#### `create_access_token(data, expires_delta)`
Creates JWT access token with expiration.

**Parameters**:
- `data: dict` - Payload to encode (typically `{"sub": user.id}`)
- `expires_delta: timedelta | None` - Custom expiration (default: 15 minutes)

**Returns**: `str` - Encoded JWT token

**Token Structure**:
```json
{
  "sub": "user_id",
  "exp": 1234567890,
  "iat": 1234567800
}
```

**Usage**:
```python
access_token = create_access_token(data={"sub": str(user.id)})
```

---

#### `create_refresh_token(db, user_id)`
Creates long-lived refresh token and stores in database.

**Parameters**:
- `db: Session` - Database session
- `user_id: int` - User ID

**Returns**: `str` - Refresh token string

**Logic**:
1. Generate secure random token (32 bytes)
2. Calculate expiration (7 days)
3. Store in `refresh_tokens` table
4. Return token

**Security**: Tokens are hashed before storage

---

#### `verify_refresh_token(db, token)`
Validates refresh token and returns user_id.

**Parameters**:
- `db: Session` - Database session
- `token: str` - Refresh token string

**Returns**: `int | None` - User ID if valid, None otherwise

**Logic**:
1. Query token from database
2. Check if expired
3. Check if revoked
4. Return user_id

---

#### `revoke_refresh_token(db, token)`
Revokes a refresh token (logout).

**Parameters**:
- `db: Session` - Database session
- `token: str` - Refresh token to revoke

**Logic**:
1. Find token in database
2. Set `revoked=True`
3. Commit transaction

---

### Security Best Practices

1. **Password Hashing**: Uses bcrypt with salt
2. **Token Expiration**: Access tokens expire in 15 minutes
3. **Refresh Rotation**: Refresh tokens can be rotated on use
4. **Token Revocation**: Logout properly revokes refresh tokens
5. **Secure Secrets**: `SECRET_KEY` from environment variables

---

## 👤 User Service

**File**: `app/services/user_service.py`
**Status**: ✅ Complete
**Tests**: ✅ 2/2 passing

### Purpose
Handles user registration, profile management, and user queries.

### Key Functions

#### `create_user(db, user_create)`
Creates a new user account.

**Parameters**:
- `db: Session` - Database session
- `user_create: UserCreate` - User data (email, username, password)

**Returns**: `User` - Created user object

**Logic**:
1. Validate email format (Pydantic)
2. Check if email already exists
3. Hash password with bcrypt
4. Create user in database
5. Return user object (without password hash)

**Validation**:
- Email must be unique
- Password minimum 8 characters (configured in schema)
- Username minimum 3 characters

**Usage**:
```python
user = create_user(db, UserCreate(
    email="new@example.com",
    username="newuser",
    password="securepass123"
))
```

---

#### `get_user_by_id(db, user_id)`
Retrieves user by ID.

**Parameters**:
- `db: Session` - Database session
- `user_id: int` - User ID

**Returns**: `User | None` - User object or None

---

#### `get_user_by_email(db, email)`
Retrieves user by email (used for login).

**Parameters**:
- `db: Session` - Database session
- `email: str` - User email

**Returns**: `User | None` - User object or None

---

#### `update_user(db, user_id, user_update)`
Updates user profile.

**Parameters**:
- `db: Session` - Database session
- `user_id: int` - User ID
- `user_update: UserUpdate` - Fields to update

**Returns**: `User` - Updated user object

**Updatable Fields**:
- `username`
- `email` (with uniqueness check)
- `height_cm`
- `weight_kg`
- `date_of_birth`
- `gender`

---

## 📅 Day Service

**File**: `app/services/day_service.py`
**Status**: ✅ Complete
**Tests**: ✅ 5/5 passing

### Purpose
Core service for daily health tracking. Manages day entities and nested relationships.

### Key Functions

#### `create_day(db, day_create, user_id)`
Creates a new day entry for a user.

**Parameters**:
- `db: Session` - Database session
- `day_create: DayCreate` - Day data (date, tags, wellness_score)
- `user_id: int` - Owner user ID

**Returns**: `Day` - Created day object

**Business Rules**:
- One day per user per date (unique constraint)
- Date cannot be in the future
- `wellness_score` must be 1-5
- `effort_score` must be 0-10 (if provided)

**Usage**:
```python
day = create_day(db, DayCreate(
    date="2025-11-02",
    tags=["workout", "healthy"],
    wellness_score=4
), user_id=1)
```

---

#### `get_day_by_date(db, user_id, date)`
Retrieves a day with all nested data (meals, exercises, water, etc.).

**Parameters**:
- `db: Session` - Database session
- `user_id: int` - User ID
- `date: str` - Date in YYYY-MM-DD format

**Returns**: `Day | None` - Day object with relationships loaded

**Performance**: Uses SQLAlchemy `joinedload()` for efficient querying.

**Loaded Relationships**:
- `day.meals` - List of meals for the day
- `day.exercises` - List of exercises
- `day.water_intakes` - Water entries
- `day.sleep_records` - Sleep data
- `day.mood_records` - Mood entries
- `day.notes` - Daily notes

**Example Response**:
```python
{
    "id": 1,
    "user_id": 1,
    "date": "2025-11-02",
    "tags": ["workout"],
    "wellness_score": 4,
    "effort_score": 8,
    "meals": [...],
    "exercises": [...],
    "water_intakes": [...],
    # ... all nested data
}
```

---

#### `get_days_by_range(db, user_id, start_date, end_date)`
Retrieves all days in a date range.

**Parameters**:
- `db: Session` - Database session
- `user_id: int` - User ID
- `start_date: str` - Start date (inclusive)
- `end_date: str` - End date (inclusive)

**Returns**: `List[Day]` - List of days with nested data

**Use Case**: Calendar view, statistics charts

**Performance**: Batch loads all nested data with joinedload()

---

#### `update_day(db, day_id, day_update, user_id)`
Updates an existing day entry.

**Parameters**:
- `db: Session` - Database session
- `day_id: int` - Day ID
- `day_update: DayUpdate` - Fields to update
- `user_id: int` - User ID (for ownership check)

**Returns**: `Day` - Updated day object

**Authorization**: Verifies day belongs to user before updating

**Updatable Fields**:
- `tags`
- `wellness_score`
- `effort_score`
- `notes_summary` (AI-generated summary)

---

#### `delete_day(db, day_id, user_id)`
Deletes a day and all nested data (CASCADE).

**Parameters**:
- `db: Session` - Database session
- `day_id: int` - Day ID
- `user_id: int` - User ID (for ownership check)

**Returns**: `None`

**Cascade Behavior**: Deletes all related meals, exercises, water, sleep, mood, notes

---

### Nested Data Pattern

FitCoach implements **nested data response pattern** for Day API:
- Day detail endpoint returns full nested structure
- Eliminates need for separate API calls for meals/exercises/etc.
- Improves frontend performance and UX
- See: [docs/architecture/nested-data-implementation.md](../docs/architecture/nested-data-implementation.md)

---

## 🍽️ Meal Service

**File**: `app/services/meal_service.py`
**Status**: ✅ Complete
**Tests**: ✅ 3/3 passing

### Purpose
Handles meal tracking, nutrition data, and meal-related queries.

### Key Functions

#### `create_meal(db, meal_create, user_id)`
Creates a new meal entry.

**Parameters**:
- `db: Session` - Database session
- `meal_create: MealCreate` - Meal data
- `user_id: int` - User ID (for day ownership verification)

**Returns**: `Meal` - Created meal object

**Business Rules**:
- Must belong to an existing day
- Day must belong to the requesting user
- Category must be: Breakfast, Lunch, Dinner, or Snack

**Nutrition Fields** (all optional):
- `calories` (integer)
- `protein_g` (float)
- `carbs_g` (float)
- `fats_g` (float)

**Usage**:
```python
meal = create_meal(db, MealCreate(
    day_id=1,
    name="Grilled Chicken Salad",
    category="Lunch",
    quantity="200g",
    calories=350,
    protein_g=40.0,
    carbs_g=15.0,
    fats_g=12.0
), user_id=1)
```

---

#### `get_meals_by_day(db, day_id, user_id)`
Retrieves all meals for a specific day.

**Parameters**:
- `db: Session` - Database session
- `day_id: int` - Day ID
- `user_id: int` - User ID (for authorization)

**Returns**: `List[Meal]` - List of meals

**Ordering**: Ordered by `created_at` (insertion order)

**Use Case**: Populating MealsSection in DayView

---

#### `update_meal(db, meal_id, meal_update, user_id)`
Updates an existing meal.

**Parameters**:
- `db: Session` - Database session
- `meal_id: int` - Meal ID
- `meal_update: MealUpdate` - Fields to update
- `user_id: int` - User ID (for ownership check)

**Returns**: `Meal` - Updated meal object

**Authorization**: Verifies meal belongs to user's day

---

#### `delete_meal(db, meal_id, user_id)`
Deletes a meal entry.

**Parameters**:
- `db: Session` - Database session
- `meal_id: int` - Meal ID
- `user_id: int` - User ID (for ownership check)

**Returns**: `None`

---

### Meal Categories

Supported categories (enum):
- `Breakfast` - Morning meals
- `Lunch` - Midday meals
- `Dinner` - Evening meals
- `Snack` - Between-meal snacks

---

## 🏃 Exercise Service

**File**: `app/services/exercise_service.py`
**Status**: ✅ Complete
**Tests**: ✅ 3/3 passing

### Purpose
Manages exercise logging, workout tracking, and activity data.

### Key Functions

#### `create_exercise(db, exercise_create, user_id)`
Creates a new exercise entry.

**Parameters**:
- `db: Session` - Database session
- `exercise_create: ExerciseCreate` - Exercise data
- `user_id: int` - User ID (for day ownership verification)

**Returns**: `Exercise` - Created exercise object

**Exercise Fields**:
- `type`: Running, Gym, Yoga, Cycling, Walking, Other
- `duration_minutes`: Required
- `distance_km`: Optional (for Running/Cycling)
- `intensity`: Low, Medium, High
- `heart_rate_avg`: Optional (BPM)
- `calories_burned`: Optional (auto-calculated or manual)
- `notes`: Optional description

**Usage**:
```python
exercise = create_exercise(db, ExerciseCreate(
    day_id=1,
    type="Running",
    duration_minutes=30,
    distance_km=5.0,
    intensity="Medium",
    heart_rate_avg=145,
    calories_burned=350
), user_id=1)
```

---

#### `get_exercises_by_day(db, day_id, user_id)`
Retrieves all exercises for a specific day.

**Parameters**:
- `db: Session` - Database session
- `day_id: int` - Day ID
- `user_id: int` - User ID (for authorization)

**Returns**: `List[Exercise]` - List of exercises

---

#### `update_exercise(db, exercise_id, exercise_update, user_id)`
Updates an existing exercise.

**Parameters**:
- `db: Session` - Database session
- `exercise_id: int` - Exercise ID
- `exercise_update: ExerciseUpdate` - Fields to update
- `user_id: int` - User ID (for ownership check)

**Returns**: `Exercise` - Updated exercise object

---

#### `delete_exercise(db, exercise_id, user_id)`
Deletes an exercise entry.

**Parameters**:
- `db: Session` - Database session
- `exercise_id: int` - Exercise ID
- `user_id: int` - User ID (for ownership check)

**Returns**: `None`

---

### Exercise Types

Supported types (enum):
- `Running` - Outdoor/treadmill running
- `Gym` - Weight training, strength exercises
- `Yoga` - Yoga, stretching, flexibility
- `Cycling` - Outdoor/indoor cycling
- `Walking` - Walking, hiking
- `Other` - Any other activity

---

## 💧 Water Service

**File**: `app/services/water_service.py`
**Status**: ✅ Complete
**Tests**: ✅ 2/2 passing

### Purpose
Tracks daily water intake with multiple entries per day.

### Key Functions

#### `create_water_intake(db, water_create, user_id)`
Creates a new water intake entry.

**Parameters**:
- `db: Session` - Database session
- `water_create: WaterIntakeCreate` - Water data (day_id, amount_ml)
- `user_id: int` - User ID (for day ownership verification)

**Returns**: `WaterIntake` - Created water intake object

**Business Rules**:
- `amount_ml` must be positive
- Multiple entries allowed per day (e.g., 250ml, 500ml, 250ml)
- Total calculated on frontend

**Usage**:
```python
water = create_water_intake(db, WaterIntakeCreate(
    day_id=1,
    amount_ml=250
), user_id=1)
```

---

#### `get_water_intakes_by_day(db, day_id, user_id)`
Retrieves all water intake entries for a day.

**Parameters**:
- `db: Session` - Database session
- `day_id: int` - Day ID
- `user_id: int` - User ID (for authorization)

**Returns**: `List[WaterIntake]` - List of water entries

**Frontend Calculation**:
```python
total_ml = sum(intake.amount_ml for intake in water_intakes)
goal_ml = 2500  # Configurable per user
percentage = (total_ml / goal_ml) * 100
```

---

#### `delete_water_intake(db, water_id, user_id)`
Deletes a water intake entry.

**Parameters**:
- `db: Session` - Database session
- `water_id: int` - Water intake ID
- `user_id: int` - User ID (for ownership check)

**Returns**: `None`

---

## 😴 Sleep Service

**File**: `app/services/sleep_service.py`
**Status**: ⏳ Placeholder (basic structure only)
**Tests**: ⏳ Not yet implemented

### Purpose
Tracks sleep duration, quality, and sleep phases.

### Planned Functions

- `create_sleep_record(db, sleep_create, user_id)` - Log sleep session
- `get_sleep_by_day(db, day_id, user_id)` - Get sleep for specific day
- `update_sleep_record(db, sleep_id, sleep_update, user_id)` - Update sleep data
- `delete_sleep_record(db, sleep_id, user_id)` - Delete sleep entry

### Planned Fields
- `start_time` (datetime)
- `end_time` (datetime)
- `duration_minutes` (calculated)
- `quality` (1-5 rating)
- `notes` (optional)

---

## 😊 Mood Service

**File**: `app/services/mood_service.py`
**Status**: ⏳ Placeholder
**Tests**: ⏳ Not yet implemented

### Purpose
Tracks daily mood, energy levels, and emotional state.

### Planned Functions

- `create_mood_record(db, mood_create, user_id)` - Log mood
- `get_moods_by_day(db, day_id, user_id)` - Get moods for day
- `update_mood_record(db, mood_id, mood_update, user_id)` - Update mood
- `delete_mood_record(db, mood_id, user_id)` - Delete mood entry

### Planned Fields
- `mood_score` (1-5)
- `tags` (array: Stress, Focus, Energy, Anxiety, Happy, Calm)
- `notes` (optional)

---

## 📝 Note Service

**File**: `app/services/note_service.py`
**Status**: ⏳ Placeholder
**Tests**: ⏳ Not yet implemented

### Purpose
Manages daily notes, journal entries, and reflections.

### Planned Functions

- `create_note(db, note_create, user_id)` - Create note
- `get_notes_by_day(db, day_id, user_id)` - Get all notes for day
- `update_note(db, note_id, note_update, user_id)` - Update note
- `delete_note(db, note_id, user_id)` - Delete note

### Planned Fields
- `content` (text, markdown support)
- `tags` (array, optional)

---

## 🎯 Goal Service

**File**: `app/services/goal_service.py`
**Status**: ⏳ Placeholder
**Tests**: ⏳ Not yet implemented

### Purpose
Manages user health goals (weight, calories, water, sleep, exercise).

### Planned Functions

- `create_goal(db, goal_create, user_id)` - Set new goal
- `get_user_goals(db, user_id)` - Get all goals for user
- `update_goal(db, goal_id, goal_update, user_id)` - Update goal
- `delete_goal(db, goal_id, user_id)` - Delete goal
- `check_goal_progress(db, user_id, goal_id, date)` - Calculate progress %

### Planned Goal Types
- Daily water intake (ml)
- Daily calories (kcal)
- Weekly exercise minutes
- Target weight (kg)
- Sleep duration (hours/night)

---

## 🤖 LLM Service

**File**: `app/services/llm_service.py`
**Status**: 📋 Planned (not yet implemented)
**Tests**: ⏳ Not yet implemented

### Purpose
Provides AI-powered insights using LangChain + OpenAI/Gemini.

### Planned Functions

#### `generate_daily_summary(db, day_id, user_id)`
Generates AI summary of the entire day.

**Input**: All day data (meals, exercises, water, sleep, mood)
**Output**: Text summary + effort score (0-10)

---

#### `analyze_meal(db, meal_id, user_id)`
Provides nutritional analysis for a specific meal.

**Input**: Meal data (name, quantity, macros)
**Output**: Insights, recommendations, balance assessment

---

#### `recommend_exercises(db, user_id)`
Suggests exercises based on user history and goals.

**Input**: User exercise history, current goals
**Output**: List of recommended exercises with reasoning

---

#### `generate_weekly_insights(db, user_id, start_date, end_date)`
Analyzes trends over a week/month.

**Input**: Date range, all health metrics
**Output**: Trends, achievements, suggestions for next period

---

### Configuration

```python
# LLM Provider
PROVIDER = "openai"  # or "gemini"

# OpenAI
OPENAI_API_KEY = "sk-..."
MODEL = "gpt-3.5-turbo"  # or "gpt-4-turbo"
TEMPERATURE = 0.7
MAX_TOKENS = 500

# Caching
CACHE_BACKEND = "redis"
CACHE_TTL = 3600  # 1 hour
```

See [docs/llm-progress.md](../docs/llm-progress.md) for full roadmap.

---

## 🔔 Notification Service

**File**: `app/services/notification_service.py`
**Status**: 📋 Planned
**Tests**: ⏳ Not yet implemented

### Purpose
Manages push notifications and in-app alerts.

### Planned Functions

- `create_notification(db, user_id, message, type)` - Create notification
- `get_user_notifications(db, user_id, unread_only)` - Fetch notifications
- `mark_as_read(db, notification_id, user_id)` - Mark notification read
- `delete_notification(db, notification_id, user_id)` - Delete notification

### Planned Notification Types
- Goal achievement
- Streak milestone
- Daily reminder
- LLM summary ready
- Low water intake alert

---

## 🔒 Authorization Pattern

All services implement **user ownership verification**:

```python
def update_resource(db, resource_id, update_data, user_id):
    # 1. Fetch resource
    resource = db.query(Resource).filter(Resource.id == resource_id).first()

    # 2. Check if exists
    if not resource:
        raise HTTPException(status_code=404, detail="Not found")

    # 3. Verify ownership (CRITICAL!)
    if resource.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 4. Perform update
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(resource, key, value)

    db.commit()
    db.refresh(resource)
    return resource
```

**Key Points**:
- Always verify `resource.user_id == user_id`
- Return 403 Forbidden if ownership check fails
- Never expose other users' data

---

## 🧪 Testing Services

All services have corresponding test files in `backend/tests/`.

### Test Structure

```python
# tests/test_meal_service.py
import pytest
from app.services.meal_service import create_meal, get_meals_by_day

def test_create_meal(db_session, test_user, test_day):
    meal_data = MealCreate(
        day_id=test_day.id,
        name="Breakfast",
        category="Breakfast",
        calories=350
    )
    meal = create_meal(db_session, meal_data, test_user.id)
    assert meal.id is not None
    assert meal.name == "Breakfast"
    assert meal.calories == 350

def test_unauthorized_access(db_session, test_user, other_user, test_meal):
    with pytest.raises(HTTPException) as exc:
        update_meal(db_session, test_meal.id, {}, other_user.id)
    assert exc.value.status_code == 403
```

### Test Coverage

Current status: **18/18 tests passing** (MVP core services)

Run tests:
```bash
cd backend
source venv/bin/activate
pytest --cov=app/services tests/
```

---

## 📚 Best Practices

### Service Design Principles

1. **Single Responsibility**: Each service handles one domain entity
2. **Dependency Injection**: Services receive `db: Session` as parameter
3. **Authorization First**: Always verify user ownership before operations
4. **Transaction Management**: Use `db.commit()` explicitly
5. **Error Handling**: Raise `HTTPException` with appropriate status codes
6. **Type Hints**: All functions use Python type hints
7. **Documentation**: Docstrings for all public functions

### Common Patterns

#### Creating Resources
```python
def create_resource(db, resource_create, user_id):
    # 1. Verify parent resource ownership (if nested)
    # 2. Create model instance
    # 3. Add to session
    # 4. Commit transaction
    # 5. Refresh to get generated fields (id, created_at)
    # 6. Return resource
```

#### Querying with Relationships
```python
def get_resource_with_nested_data(db, resource_id):
    return db.query(Resource).options(
        joinedload(Resource.nested_items)
    ).filter(Resource.id == resource_id).first()
```

#### Updating Resources
```python
def update_resource(db, resource_id, update_data, user_id):
    # 1. Fetch resource
    # 2. Verify ownership
    # 3. Apply updates only for provided fields (exclude_unset=True)
    # 4. Commit and refresh
    # 5. Return updated resource
```

---

## 🔗 Related Documentation

- [Backend README](./README.md) - API overview and setup
- [API Specification](../docs/api-specification.md) - OpenAPI 3.0 spec
- [Database Schema](../docs/database-schema.md) - Model relationships
- [Architecture Decisions](../docs/architecture-decisions.md) - ADRs
- [LLM Integration Progress](../docs/llm-progress.md) - AI features roadmap

---

**Last Updated**: 2025-11-02
**Status**: Living Document - Update as services evolve
