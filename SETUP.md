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

### 3. Configure Environment Variables

The Desktop app uses environment variables for configuration. This is the **RECOMMENDED** approach to avoid hardcoded URLs.

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env if needed (default values work for local development)
nano .env
```

**Default `.env` contents:**
```env
# Backend API base URL
VITE_API_BASE_URL=http://localhost:8001/api/v1

# Application configuration
VITE_APP_NAME=FitCoach
VITE_APP_VERSION=0.1.0
VITE_APP_ENV=development
```

**How it works:**
- The API client (`src/services/api/client.ts`) automatically reads `VITE_API_BASE_URL`
- If not set, it falls back to `http://localhost:8001/api/v1`
- Variables must be prefixed with `VITE_` to be exposed to the client
- Never commit `.env` files to Git (they're in `.gitignore`)

**For production:**
```bash
cp .env.production.example .env.production
# Edit .env.production with your production API URL
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

**Before building for production:**

1. Create production environment file:
   ```bash
   cp .env.production.example .env.production
   ```

2. Update with your production API URL:
   ```bash
   nano .env.production
   # Set: VITE_API_BASE_URL=https://api.fitcoach.com/api/v1
   ```

3. Build the application:
   ```bash
   # Build for current platform
   npm run build
   npm run package

   # Build for specific platform
   npm run package:linux

   # Output will be in /release directory
   ```

---

## Mobile Setup

### 1. Navigate to Mobile Directory
```bash
cd /path/to/fit-coach/mobile
```

### 2. Install Dependencies
```bash
npm install
```

This will install:
- React Native (Expo)
- TypeScript
- React Navigation
- Axios
- expo-constants (for environment variables)
- And other dependencies from `package.json`

### 3. Configure Environment Variables

The Mobile app uses environment variables for configuration.

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**For Simulator/Emulator (localhost works):**
```env
EXPO_PUBLIC_API_BASE_URL=http://localhost:8001/api/v1
```

**For Physical Device (use your computer's local IP):**
```bash
# Find your local IP
# macOS/Linux:
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows:
ipconfig
```

Update `.env`:
```env
# Replace with your actual IP address
EXPO_PUBLIC_API_BASE_URL=http://192.168.1.100:8001/api/v1
```

**How it works:**
- The API client (`src/services/api/apiClient.ts`) reads `EXPO_PUBLIC_API_BASE_URL`
- Variables are also available via `Constants.expoConfig.extra` (configured in `app.config.js`)
- Variables must be prefixed with `EXPO_PUBLIC_`
- Never commit `.env` files to Git (they're in `.gitignore`)

**Important for device testing:**
- Your device and computer must be on the same Wi-Fi network
- Backend server must be accessible from your device
- Firewall must allow connections on port 8001

**For production:**
```bash
cp .env.production.example .env.production
# Edit .env.production with your production API URL
```

### 4. Start Mobile Development Server

```bash
# Start Expo development server
npm start

# Or run on specific platform
npm run ios      # iOS Simulator (macOS only)
npm run android  # Android Emulator
npm run web      # Web browser (for testing)
```

### 5. Testing on Physical Devices

1. Install **Expo Go** app on your device:
   - iOS: [App Store](https://apps.apple.com/app/expo-go/id982107779)
   - Android: [Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. Ensure device and computer are on same Wi-Fi

3. Scan QR code from terminal with Expo Go app

4. If connection fails, update `.env` with your local IP address

---

## Full-Stack Development

To run backend, desktop, and mobile simultaneously:

### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate
python main.py
```

### Terminal 2: Desktop (Optional)
```bash
cd desktop
# Make sure .env is configured
npm run dev
```

### Terminal 3: Mobile (Optional)
```bash
cd mobile
# Make sure .env is configured
npm start
```

### Terminal 4: Database (if using Docker)
```bash
cd backend
docker-compose up
```

### Typical Development Flow

1. **Configure Environment Variables** → Set up `.env` files for Desktop and Mobile
2. **Start Backend** → Wait for "Application startup complete"
3. **Start Desktop and/or Mobile** → Applications connect to backend
4. **Register a user** → Use Desktop/Mobile UI or Swagger UI
5. **Login** → JWT tokens stored securely
6. **Create daily entries** → Track meals, exercises, etc.
7. **Test API** → Use Swagger UI at http://localhost:8001/docs

### Environment Configuration Summary

| Component | Config File | API URL Variable | Default Value |
|-----------|-------------|------------------|---------------|
| **Backend** | `.env` | `POSTGRES_SERVER`, etc. | Various |
| **Desktop** | `.env` | `VITE_API_BASE_URL` | `http://localhost:8001/api/v1` |
| **Mobile** | `.env` | `EXPO_PUBLIC_API_BASE_URL` | `http://localhost:8001/api/v1` |

**Key Points:**
- All `.env` files are in `.gitignore` (never committed)
- All `.env.example` files are committed as documentation
- Copy `.env.example` to `.env` and customize as needed
- For production, create `.env.production` with production URLs

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
**Solution**: Backend is not running or wrong API URL:
```bash
# Option 1: Start backend
cd backend
source venv/bin/activate
python main.py

# Option 2: Check .env configuration
cat .env | grep VITE_API_BASE_URL
# Should match your backend URL
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

### Mobile Issues

#### 1. "Network Error" when testing on device
**Solution**: Update API URL in `.env` to use your computer's local IP:
```bash
# Find your local IP
ifconfig | grep "inet " | grep -v 127.0.0.1  # macOS/Linux
ipconfig  # Windows

# Update .env
EXPO_PUBLIC_API_BASE_URL=http://192.168.1.100:8001/api/v1
```

#### 2. "Cannot connect to Expo Dev Server"
**Solution**: Ensure device and computer are on same Wi-Fi:
```bash
# Option 1: Try tunnel mode
expo start --tunnel

# Option 2: Check firewall settings
# Ensure ports 8001 and 19000-19006 are open
```

### Common Issues

#### 1. "API URL not updating after .env change"
**Solution**: Restart development server after changing `.env`:
```bash
# Desktop
npm run dev  # Restart

# Mobile
npm start  # Restart and clear cache
```

#### 2. "Permission denied" when running scripts
**Solution**: Make scripts executable:
```bash
chmod +x script_name.sh
```

#### 3. CORS errors in browser console
**Solution**: Check backend CORS settings in `app/core/config.py`:
```python
BACKEND_CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
```

#### 4. "Environment variable not defined"
**Solution**: Ensure `.env` file exists and variables are prefixed correctly:
```bash
# Desktop: Variables must start with VITE_
VITE_API_BASE_URL=http://localhost:8001/api/v1

# Mobile: Variables must start with EXPO_PUBLIC_
EXPO_PUBLIC_API_BASE_URL=http://localhost:8001/api/v1

# Check if .env exists
ls -la .env
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
