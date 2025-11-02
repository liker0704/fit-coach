# FitCoach Setup Guide

Complete setup instructions for all FitCoach components: Backend API, Desktop Client, and development environment.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Desktop Setup](#desktop-setup)
- [Full-Stack Development](#full-stack-development)
- [Docker Compose Setup](#docker-compose-setup-optional)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

**For Backend Development:**
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/) or use Docker
- **Docker & Docker Compose** - [Download](https://docs.docker.com/get-docker/)

**For Desktop Development:**
- **Node.js 18+** - [Download](https://nodejs.org/) (LTS recommended)
- **npm 9+** - Comes with Node.js

**Recommended Tools:**
- **Git** - Version control
- **VS Code** - Code editor with Python and TypeScript extensions
- **Postman/Insomnia** - API testing (optional, Swagger UI is included)

### System Requirements
- **OS**: Linux, macOS, or Windows 10/11
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space for dependencies and database

---

## Backend Setup

### 1. Navigate to Backend Directory
```bash
cd /path/to/fit-coach/backend
```

### 2. Create Python Virtual Environment
```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required `.env` settings:**
```env
# API Settings
PROJECT_NAME=FitCoach
VERSION=0.1.0

# Security - IMPORTANT: Change in production!
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=fitcoach
POSTGRES_PASSWORD=fitcoach_password
POSTGRES_DB=fitcoach
POSTGRES_PORT=5432

# Redis (for future caching)
REDIS_HOST=localhost
REDIS_PORT=6379

# LLM Configuration (optional, for future AI features)
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL_NAME=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=500
```

**🔒 Security Note**: Generate a secure `SECRET_KEY` for production:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Start PostgreSQL Database

**Option A: Using Docker Compose (Recommended)**
```bash
# Start PostgreSQL + Redis
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres
```

**Option B: Using Local PostgreSQL**
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE fitcoach;
CREATE USER fitcoach WITH PASSWORD 'fitcoach_password';
GRANT ALL PRIVILEGES ON DATABASE fitcoach TO fitcoach;
\q
```

### 6. Run Database Migrations
```bash
# Ensure venv is activated
source venv/bin/activate

# Run migrations to create tables
alembic upgrade head

# Verify migration status
alembic current
```

### 7. Start Backend Server
```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### 8. Verify Backend is Running

Open in browser:
- **API Docs (Swagger)**: http://localhost:8001/docs
- **API Docs (ReDoc)**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/api/v1/health

### 9. Run Backend Tests (Optional)
```bash
# Ensure venv is activated
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

**Expected result**: 18/18 tests passing ✅

---

## Desktop Setup

### 1. Navigate to Desktop Directory
```bash
cd /path/to/fit-coach/desktop
```

### 2. Install Node Dependencies
```bash
npm install
```

This will install:
- Electron 39 (desktop framework)
- React 19 (UI library)
- TypeScript 5.8 (type-safe JavaScript)
- TailwindCSS 3.4 (styling)
- shadcn/ui (component library)
- Zustand 5.0 (state management)
- Axios (HTTP client)
- And other dependencies from `package.json`

### 3. Configure Backend API URL (Optional)

The default backend URL is `http://localhost:8001`. If your backend runs on a different port, update:

```typescript
// src/services/api.ts
const BASE_URL = process.env.VITE_API_URL || 'http://localhost:8001';
```

Or create `.env.local`:
```env
VITE_API_URL=http://localhost:8001
```

### 4. Start Desktop Development Server
```bash
npm run dev
```

This starts:
- **Vite dev server** on http://localhost:5173 (React app)
- **Electron app** (desktop window)

**Expected output:**
```
VITE v7.0.4  ready in 423 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help

[Electron] App started in development mode
```

### 5. Access Desktop App

The Electron window should open automatically. If not:
- Open http://localhost:5173 in your browser (for web development)
- Or restart `npm run dev`

### 6. Build Desktop App for Production (Optional)

```bash
# Build for current platform
npm run build
npm run package

# Build for specific platform
npm run package:linux

# Output will be in /release directory
```

---

## Full-Stack Development

To run both backend and desktop simultaneously:

### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate
python main.py
```

### Terminal 2: Desktop
```bash
cd desktop
npm run dev
```

### Terminal 3: Database (if using Docker)
```bash
cd backend
docker-compose up
```

### Typical Development Flow

1. **Start Backend** → Wait for "Application startup complete"
2. **Start Desktop** → Electron window opens
3. **Register a user** → Use desktop UI or Swagger UI
4. **Login** → JWT tokens stored in localStorage
5. **Create daily entries** → Track meals, exercises, etc.
6. **Test API** → Use Swagger UI at http://localhost:8001/docs

---

## Docker Compose Setup (Optional)

For easier backend infrastructure management:

### 1. Full Stack with Docker

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: fitcoach-db
    environment:
      POSTGRES_USER: fitcoach
      POSTGRES_PASSWORD: fitcoach_password
      POSTGRES_DB: fitcoach
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fitcoach"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: fitcoach-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: fitcoach-backend
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      POSTGRES_SERVER: postgres
      POSTGRES_USER: fitcoach
      POSTGRES_PASSWORD: fitcoach_password
      POSTGRES_DB: fitcoach
      REDIS_HOST: redis
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key}
    ports:
      - "8001:8001"
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

volumes:
  postgres_data:
```

### 2. Start Full Stack
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (data will be lost!)
docker-compose down -v
```

---

## Troubleshooting

### Backend Issues

#### 1. "ImportError: No module named 'app'"
**Solution**: Ensure you're in the `backend/` directory and venv is activated:
```bash
cd backend
source venv/bin/activate
python main.py
```

#### 2. "sqlalchemy.exc.OperationalError: could not connect to server"
**Solution**: PostgreSQL is not running or wrong credentials:
```bash
# Check Docker containers
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres

# Check .env database settings
cat .env | grep POSTGRES
```

#### 3. "alembic.util.exc.CommandError: Can't locate revision"
**Solution**: Database needs migration:
```bash
alembic upgrade head
```

#### 4. Tests failing with "Database already exists"
**Solution**: Use separate test database or reset:
```bash
# Option 1: Configure test database in pytest.ini
# Option 2: Reset database
alembic downgrade base
alembic upgrade head
```

### Desktop Issues

#### 1. "Cannot find module '@/components/ui/button'"
**Solution**: shadcn/ui components not installed:
```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
# ... install other needed components
```

#### 2. "ECONNREFUSED 127.0.0.1:8001"
**Solution**: Backend is not running:
```bash
# Start backend first
cd backend
source venv/bin/activate
python main.py
```

#### 3. "Electron failed to start"
**Solution**: Clean installation:
```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

#### 4. "401 Unauthorized" after login
**Solution**: Check JWT token storage and expiration:
```javascript
// Open browser DevTools → Application → Local Storage
// Verify 'auth-storage' exists with valid tokens
// If expired, login again
```

### Database Issues

#### 1. "psycopg2.OperationalError: FATAL: role 'fitcoach' does not exist"
**Solution**: Create PostgreSQL user:
```bash
sudo -u postgres psql
CREATE USER fitcoach WITH PASSWORD 'fitcoach_password';
GRANT ALL PRIVILEGES ON DATABASE fitcoach TO fitcoach;
\q
```

#### 2. "relation 'users' does not exist"
**Solution**: Run migrations:
```bash
alembic upgrade head
```

#### 3. Port 5432 already in use
**Solution**: Another PostgreSQL instance is running:
```bash
# Find process
sudo lsof -i :5432

# Stop system PostgreSQL
sudo systemctl stop postgresql

# Or change port in .env and docker-compose.yml
POSTGRES_PORT=5433
```

### Common Issues

#### 1. "Permission denied" when running scripts
**Solution**: Make scripts executable:
```bash
chmod +x script_name.sh
```

#### 2. CORS errors in browser console
**Solution**: Check backend CORS settings in `app/core/config.py`:
```python
BACKEND_CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
```

#### 3. Slow performance on Linux (charts)
**Solution**: This was the reason for Electron migration. Ensure you're using Electron, not Tauri. See [desktop/ELECTRON_MIGRATION.md](./desktop/ELECTRON_MIGRATION.md).

---

## Next Steps

After successful setup:

1. **Backend**: Create your first user via Swagger UI at http://localhost:8001/docs
2. **Desktop**: Login and create a daily entry with meals/exercises
3. **Explore API**: Try different endpoints in Swagger UI
4. **Run Tests**: Ensure everything works with `pytest` in backend
5. **Read Documentation**: Check [backend/README.md](./backend/README.md) and [desktop/README.md](./desktop/README.md)

---

## Additional Resources

- **Backend API Docs**: [backend/README.md](./backend/README.md)
- **Desktop Client Docs**: [desktop/README.md](./desktop/README.md)
- **Architecture Decisions**: [docs/architecture-decisions.md](./docs/architecture-decisions.md)
- **API Specification**: [docs/api-specification.md](./docs/api-specification.md)
- **Database Schema**: [docs/database-schema.md](./docs/database-schema.md)

---

## Support

If you encounter issues not covered here:
1. Check existing [GitHub Issues](https://github.com/yourusername/fit-coach/issues)
2. Review component-specific README files
3. Open a new issue with detailed error logs

**Happy coding! 🚀**
