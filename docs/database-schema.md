# Database Schema - PostgreSQL

## Полная схема базы данных FitCoach

### ERD Diagram
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    users     │────<│     days     │────<│    meals     │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                     │
       │                    ├────────────<────────┤
       │                    │                meal_items
       │                    │
       │                    ├────<────── exercises
       │                    │                │
       │                    │                ├──< exercise_sets
       │                    │
       │                    ├────<────── water_intakes
       │                    │
       │                    ├────<────── sleep_records
       │                    │
       │                    ├────<────── mood_records
       │                    │
       │                    ├────<────── notes
       │                    │
       │                    └────<────── llm_summaries
       │
       ├────<────── goals
       ├────<────── refresh_tokens
       ├────<────── notifications
       └────<────── user_settings
```

## Таблицы

### users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),

    -- Profile
    age INTEGER CHECK (age > 0 AND age < 150),
    height DECIMAL(5,2), -- cm
    weight DECIMAL(5,2), -- kg
    target_weight DECIMAL(5,2),

    -- Settings
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    water_goal DECIMAL(3,1) DEFAULT 2.5, -- liters
    calorie_goal INTEGER DEFAULT 2000,
    sleep_goal DECIMAL(3,1) DEFAULT 8.0, -- hours

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    last_login TIMESTAMPTZ,

    -- Indexes
    INDEX idx_users_email (email),
    INDEX idx_users_username (username),
    INDEX idx_users_active (is_active)
);
```

### days
```sql
CREATE TABLE days (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,

    -- Metrics
    tag VARCHAR(50),
    feeling INTEGER CHECK (feeling >= 1 AND feeling <= 5),
    effort_score DECIMAL(3,1) CHECK (effort_score >= 0 AND effort_score <= 10),

    -- Summary
    summary TEXT,
    llm_advice TEXT,

    -- Constraints
    UNIQUE(user_id, date),

    -- Indexes
    INDEX idx_days_user_date (user_id, date),
    INDEX idx_days_date (date),
    INDEX idx_days_effort (effort_score)
);
```

### meals
```sql
CREATE TABLE meals (
    id SERIAL PRIMARY KEY,
    day_id INTEGER NOT NULL REFERENCES days(id) ON DELETE CASCADE,

    category VARCHAR(20) NOT NULL CHECK (category IN ('breakfast', 'lunch', 'dinner', 'snack')),
    time TIME,

    -- Nutrition
    calories DECIMAL(7,2),
    protein DECIMAL(6,2), -- grams
    carbs DECIMAL(6,2),
    fat DECIMAL(6,2),
    fiber DECIMAL(5,2),
    sugar DECIMAL(5,2),
    sodium DECIMAL(7,2), -- mg

    -- Details
    notes TEXT,
    photo_url VARCHAR(500),

    -- AI
    ai_summary TEXT,
    ai_suggestions TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes
    INDEX idx_meals_day (day_id),
    INDEX idx_meals_category (category)
);
```

### meal_items
```sql
CREATE TABLE meal_items (
    id SERIAL PRIMARY KEY,
    meal_id INTEGER NOT NULL REFERENCES meals(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    amount DECIMAL(7,2),
    unit VARCHAR(20), -- g, ml, cup, piece
    calories DECIMAL(7,2),

    -- Nutrition (optional)
    protein DECIMAL(6,2),
    carbs DECIMAL(6,2),
    fat DECIMAL(6,2),

    -- Indexes
    INDEX idx_meal_items_meal (meal_id),
    INDEX idx_meal_items_name (name)
);
```

### exercises
```sql
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    day_id INTEGER NOT NULL REFERENCES days(id) ON DELETE CASCADE,

    type VARCHAR(50) NOT NULL, -- running, gym, yoga, cycling
    name VARCHAR(255),

    -- Time
    start_time TIMESTAMPTZ,
    duration INTEGER, -- minutes

    -- Metrics
    distance DECIMAL(6,2), -- km
    calories_burned DECIMAL(7,2),
    heart_rate_avg INTEGER,
    heart_rate_max INTEGER,
    intensity INTEGER CHECK (intensity >= 1 AND intensity <= 5),

    -- Details
    notes TEXT,

    -- AI
    ai_feedback TEXT,
    ai_recommendations TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes
    INDEX idx_exercises_day (day_id),
    INDEX idx_exercises_type (type)
);
```

### exercise_sets
```sql
CREATE TABLE exercise_sets (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,

    set_number INTEGER NOT NULL,
    exercise_name VARCHAR(255),
    reps INTEGER,
    weight DECIMAL(5,2), -- kg
    rest_seconds INTEGER,

    -- Indexes
    INDEX idx_sets_exercise (exercise_id)
);
```

### water_intakes
```sql
CREATE TABLE water_intakes (
    id SERIAL PRIMARY KEY,
    day_id INTEGER NOT NULL REFERENCES days(id) ON DELETE CASCADE,

    amount DECIMAL(3,2) NOT NULL, -- liters
    time TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes
    INDEX idx_water_day (day_id),
    INDEX idx_water_time (time)
);
```

### sleep_records
```sql
CREATE TABLE sleep_records (
    id SERIAL PRIMARY KEY,
    day_id INTEGER NOT NULL REFERENCES days(id) ON DELETE CASCADE,

    bedtime TIMESTAMPTZ,
    wake_time TIMESTAMPTZ,
    duration DECIMAL(4,2), -- hours (calculated)

    quality INTEGER CHECK (quality >= 1 AND quality <= 5),
    deep_sleep DECIMAL(4,2), -- hours
    rem_sleep DECIMAL(4,2), -- hours

    interruptions INTEGER DEFAULT 0,
    notes TEXT,

    -- AI
    ai_analysis TEXT,
    ai_recommendations TEXT,

    -- Indexes
    INDEX idx_sleep_day (day_id)
);
```

### mood_records
```sql
CREATE TABLE mood_records (
    id SERIAL PRIMARY KEY,
    day_id INTEGER NOT NULL REFERENCES days(id) ON DELETE CASCADE,

    time TIMESTAMPTZ DEFAULT NOW(),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),

    -- Levels
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 5),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 5),
    anxiety_level INTEGER CHECK (anxiety_level >= 1 AND anxiety_level <= 5),

    tags JSONB, -- ["happy", "tired", "stressed", "focused"]
    notes TEXT,

    -- AI
    ai_sentiment VARCHAR(50),
    ai_suggestions TEXT,

    -- Indexes
    INDEX idx_mood_day (day_id),
    INDEX idx_mood_time (time),
    INDEX idx_mood_tags (tags) USING gin
);
```

### notes
```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    day_id INTEGER NOT NULL REFERENCES days(id) ON DELETE CASCADE,

    title VARCHAR(255),
    content TEXT NOT NULL, -- Markdown

    tags JSONB,
    attachments JSONB, -- URLs to files

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,

    -- Indexes
    INDEX idx_notes_day (day_id),
    INDEX idx_notes_created (created_at),
    INDEX idx_notes_tags (tags) USING gin
);
```

### llm_summaries
```sql
CREATE TABLE llm_summaries (
    id SERIAL PRIMARY KEY,
    day_id INTEGER NOT NULL REFERENCES days(id) ON DELETE CASCADE,

    -- Main summary
    summary_text TEXT NOT NULL,
    effort_score DECIMAL(3,1) NOT NULL CHECK (effort_score >= 0 AND effort_score <= 10),
    score_reason TEXT,

    -- Detailed analysis
    nutrition_analysis TEXT,
    exercise_analysis TEXT,
    sleep_analysis TEXT,
    mood_analysis TEXT,

    -- Recommendations
    tomorrow_advice TEXT,
    weekly_goals JSONB,

    -- Meta
    model_used VARCHAR(50),
    prompt_version VARCHAR(20),
    tokens_used INTEGER,
    generation_time DECIMAL(6,2), -- seconds

    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(day_id),

    -- Indexes
    INDEX idx_llm_day (day_id),
    INDEX idx_llm_created (created_at)
);
```

### goals
```sql
CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    type VARCHAR(50) NOT NULL, -- weight, exercise, water, sleep, calories
    title VARCHAR(255) NOT NULL,
    description TEXT,

    target_value DECIMAL(10,2),
    current_value DECIMAL(10,2) DEFAULT 0,
    unit VARCHAR(20),

    start_date DATE NOT NULL,
    end_date DATE,

    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived')),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Indexes
    INDEX idx_goals_user (user_id),
    INDEX idx_goals_status (status),
    INDEX idx_goals_type (type)
);
```

### refresh_tokens
```sql
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes
    INDEX idx_refresh_user (user_id),
    INDEX idx_refresh_token (token),
    INDEX idx_refresh_expires (expires_at)
);
```

### notifications
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,

    data JSONB,

    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes
    INDEX idx_notif_user (user_id),
    INDEX idx_notif_read (is_read),
    INDEX idx_notif_created (created_at)
);
```

## Миграции Alembic

### Начальная миграция
```python
"""Initial migration

Revision ID: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        # ... остальные поля
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])

    # Create other tables...

def downgrade():
    op.drop_table('users')
    # Drop other tables...
```

## Оптимизация

### Индексы производительности
```sql
-- Композитные индексы для частых запросов
CREATE INDEX idx_days_user_date_range ON days(user_id, date DESC);
CREATE INDEX idx_meals_day_category ON meals(day_id, category);
CREATE INDEX idx_exercises_day_type ON exercises(day_id, type);

-- Partial indexes
CREATE INDEX idx_goals_active ON goals(user_id) WHERE status = 'active';
CREATE INDEX idx_notifications_unread ON notifications(user_id) WHERE is_read = FALSE;

-- Full-text search
ALTER TABLE notes ADD COLUMN search_vector tsvector;
CREATE INDEX idx_notes_search ON notes USING gin(search_vector);

-- Update trigger for search vector
CREATE OR REPLACE FUNCTION notes_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.content, '')), 'B');
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER notes_search_update
    BEFORE INSERT OR UPDATE ON notes
    FOR EACH ROW EXECUTE FUNCTION notes_search_trigger();
```

### Партиционирование
```sql
-- Партиционирование таблицы days по месяцам
CREATE TABLE days_2024_01 PARTITION OF days
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE days_2024_02 PARTITION OF days
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

## Seed Data
```sql
-- Создание тестового пользователя
INSERT INTO users (email, username, hashed_password, full_name)
VALUES ('test@example.com', 'testuser', '$2b$12$...', 'Test User');

-- Создание тестовых дней
INSERT INTO days (user_id, date, tag, feeling, effort_score)
VALUES
    (1, '2024-01-01', 'New Year', 5, 8.5),
    (1, '2024-01-02', 'Back to work', 3, 6.0);

-- Создание тестовых приемов пищи
INSERT INTO meals (day_id, category, calories, protein, carbs, fat)
VALUES
    (1, 'breakfast', 450, 20, 60, 15),
    (1, 'lunch', 650, 35, 70, 25),
    (1, 'dinner', 550, 40, 50, 20);
```

## Backup и восстановление
```bash
# Backup
pg_dump -h localhost -U postgres -d fitcoach > backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U postgres -d fitcoach < backup_20240101.sql

# Backup только структуры
pg_dump -h localhost -U postgres -d fitcoach --schema-only > schema.sql

# Backup только данных
pg_dump -h localhost -U postgres -d fitcoach --data-only > data.sql
```