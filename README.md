# FitCoach

**Cross-platform Personal Health Tracker with AI Coach**

[![Backend Tests](https://img.shields.io/badge/Backend-18%2F18%20tests%20passing-success.svg)](./backend/TEST_REPORT.md)
[![Backend Status](https://img.shields.io/badge/Backend-MVP%20Complete-success.svg)](#backend)
[![Desktop Status](https://img.shields.io/badge/Desktop-In%20Development-yellow.svg)](#desktop)
[![iOS Status](https://img.shields.io/badge/iOS-Planned-lightgrey.svg)](#ios)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

## 📋 Overview

FitCoach is a comprehensive cross-platform health tracking system with native clients for Desktop (Linux/Windows/macOS) and iOS. All data is stored on a secure server with FastAPI backend and PostgreSQL database. The application enables tracking of daily habits, health metrics, and provides AI-powered coaching insights using LangChain + OpenAI.

**Project Status**: Backend MVP complete, Desktop in active development, iOS in planning phase.

## 🏗️ Architecture

```
┌──────────────────────────────────┐
│  Desktop App (Electron + React)  │
│  - LocalStorage cache            │
│  - REST API → FastAPI            │
└────────────┬─────────────────────┘
             │ HTTPS / JWT
┌────────────▼─────────────────────┐
│      FastAPI Backend (Python)    │
│  - JWT Authentication            │
│  - SQLAlchemy ORM                │
│  - LangChain + OpenAI (planned)  │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│      PostgreSQL Database         │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│   iOS App (Swift / SwiftUI)      │
│   - CoreData / SQLite cache      │
│   - REST API → FastAPI           │
└──────────────────────────────────┘
```

## ✨ Key Features

### Core Functionality
- **Daily Tracking Card** - Date, tags, wellness score, effort rating
- **Nutrition Logging** - Meals with macronutrients, calories, categories
- **Exercise Tracking** - Workouts with duration, intensity, heart rate
- **Water Intake** - Visual hydration monitoring (goal: 2.5-3L)
- **Sleep Tracking** - Duration, quality rating, sleep phases
- **Mood Tracking** - 1-5 scale with tags (stress, focus, energy)
- **Notes** - Markdown editor for daily reflections
- **AI Coach** (planned) - LLM-powered daily summaries and recommendations

### Statistics & Analytics
- Weight, distance, calories, water, sleep, effort graphs
- Weekly/monthly aggregations
- Trend analysis and progress visualization

### Security & Privacy
- JWT-based authentication (access + refresh tokens)
- Password hashing with bcrypt
- User data isolation
- CORS protection
- Secure token storage

## 🚀 Quick Start

### Prerequisites
- **Backend**: Python 3.11+, PostgreSQL 15+, Docker & Docker Compose
- **Desktop**: Node.js 18+, npm 9+

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fit-coach
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   cp .env.example .env  # Configure your settings
   docker-compose up -d  # Start PostgreSQL
   alembic upgrade head  # Run migrations
   python main.py  # Start server at http://localhost:8001
   ```

3. **Desktop Setup**
   ```bash
   cd desktop
   npm install
   npm run dev  # Start at http://localhost:5173
   ```

For detailed setup instructions, see [SETUP.md](./SETUP.md).

## 📁 Project Structure

```
fit-coach/
├── backend/              # FastAPI REST API
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Config, security, database
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # Business logic
│   ├── alembic/         # Database migrations
│   ├── tests/           # Pytest test suite
│   └── README.md        # Backend documentation
│
├── desktop/             # Electron + React client
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API client
│   │   ├── store/       # Zustand state management
│   │   └── types/       # TypeScript types
│   ├── electron/        # Electron main process
│   └── README.md        # Desktop documentation
│
├── ios/                 # iOS Swift client (planned)
│   └── README.md        # iOS development plan
│
└── docs/                # Project documentation
    ├── README.md                    # Documentation index
    ├── architecture-decisions.md    # ADRs
    ├── api-specification.md         # OpenAPI 3.0 spec
    ├── database-schema.md           # Database design
    ├── implementation-plan.md       # Task breakdown (550+ tasks)
    └── llm-progress.md              # AI features tracking
```

## 🔧 Technology Stack

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | **FastAPI** | REST API framework |
| Database | **PostgreSQL 15+** | Relational data storage |
| ORM | **SQLAlchemy 2.0** | Database abstraction |
| Migrations | **Alembic** | Schema version control |
| Auth | **JWT (python-jose)** | Stateless authentication |
| Validation | **Pydantic v2** | Request/response validation |
| Testing | **Pytest** | Unit & integration tests |

### Desktop
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | **Electron 39** | Cross-platform desktop app |
| UI Framework | **React 19** | Component-based UI |
| Language | **TypeScript 5.8** | Type-safe development |
| Styling | **TailwindCSS 3.4** | Utility-first CSS |
| Components | **shadcn/ui** | High-quality UI components |
| State | **Zustand 5.0** | Lightweight state management |
| Router | **React Router 7** | Client-side routing |
| Charts | **Recharts** | Data visualization |
| HTTP Client | **Axios** | API communication |

### iOS (Planned)
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | **Swift + SwiftUI** | Native iOS UI |
| Networking | **URLSession / Alamofire** | REST API client |
| Storage | **CoreData / GRDB** | Local cache |
| Charts | **Swift Charts** | Data visualization |

## 📖 Documentation

- **[SETUP.md](./SETUP.md)** - Comprehensive setup guide for all platforms
- **[project.md](./project.md)** - Complete technical specification (Russian)
- **[docs/](./docs/)** - Detailed documentation
  - [Architecture Decisions](./docs/architecture-decisions.md) - ADRs explaining key choices
  - [API Specification](./docs/api-specification.md) - OpenAPI 3.0 REST API docs
  - [Database Schema](./docs/database-schema.md) - Database design & relationships
  - [Implementation Plan](./docs/implementation-plan.md) - 550+ atomic tasks breakdown
- **[backend/README.md](./backend/README.md)** - Backend API documentation
- **[desktop/README.md](./desktop/README.md)** - Desktop client documentation
- **[desktop/ELECTRON_MIGRATION.md](./desktop/ELECTRON_MIGRATION.md)** - Tauri to Electron migration details

## 🧪 Testing

### Backend
```bash
cd backend
source venv/bin/activate
pytest  # Run all tests (18/18 passing)
pytest --cov=app tests/  # With coverage report
```

See [backend/TEST_REPORT.md](./backend/TEST_REPORT.md) for detailed test results.

### Desktop
```bash
cd desktop
npm test  # Run tests (when implemented)
```

## 🗺️ Roadmap

### ✅ Completed
- [x] Backend MVP with core models (User, Day, Meal, Exercise, Water, Sleep, Mood)
- [x] JWT authentication with refresh tokens
- [x] Database schema & migrations
- [x] API documentation (Swagger/OpenAPI)
- [x] Backend test suite (18/18 passing)
- [x] Desktop foundation (Electron + React + TypeScript)
- [x] State management & API integration
- [x] Tauri → Electron migration for better performance

### 🔨 In Progress
- [ ] Desktop UI implementation (auth, calendar, day view, statistics)
- [ ] shadcn/ui component integration
- [ ] Calendar view with monthly grid
- [ ] Day detail view with 7 sections

### 📅 Planned
- [ ] LLM integration (LangChain + OpenAI)
- [ ] AI-powered daily summaries
- [ ] Effort score calculation
- [ ] iOS native client
- [ ] Data export/import (JSON)
- [ ] Multi-language support (EN/RU/CZ)
- [ ] Dark mode theme

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- Git workflow & branching strategy
- Conventional commit guidelines
- Code style standards
- Testing requirements
- Pull request process

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🔗 Links

- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs (Swagger UI)
- **Desktop App**: http://localhost:5173 (dev server)
- **Issue Tracker**: [GitHub Issues](https://github.com/yourusername/fit-coach/issues)

## 💡 Key Design Decisions

### Why Electron over Tauri?
The project recently migrated from Tauri to Electron due to performance issues with complex SVG rendering (7+ Recharts charts) in WebKitGTK on Linux. Electron provides consistent Chromium-based rendering across all platforms with hardware acceleration. See [desktop/ELECTRON_MIGRATION.md](./desktop/ELECTRON_MIGRATION.md) for details.

### Why FastAPI?
FastAPI provides automatic API documentation, excellent performance, native async support, and Pydantic validation out of the box - perfect for building modern REST APIs.

### Why PostgreSQL?
PostgreSQL offers robust JSONB support for nested data structures, excellent performance, and is free for enterprise use. Essential for storing complex health tracking data with flexible schemas.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for better health tracking**
