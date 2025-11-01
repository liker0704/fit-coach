# FitCoach Desktop

**Personal Health Tracker - Native Desktop Client (Tauri + React + TypeScript)**

[![Tauri](https://img.shields.io/badge/Tauri-2.0+-blue.svg)](https://tauri.app)
[![React](https://img.shields.io/badge/React-18.3+-61dafb.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-blue.svg)](https://www.typescriptlang.org)
[![Status](https://img.shields.io/badge/Status-Foundation%20Complete-success.svg)](#)

## 📋 Overview

FitCoach Desktop is a native cross-platform desktop application for personal health tracking with AI-powered coaching. Built with Tauri and React, it provides a modern, responsive interface for managing daily health metrics including meals, exercises, water intake, sleep, mood, and notes.

**Status**: ✅ Foundation Complete - UI Development Ready

**Backend API**: Requires FitCoach backend running on http://localhost:8001

## ✨ Features

### ✅ Implemented (Foundation)

**Technical Infrastructure**
- ✅ Tauri 2.0 - Native desktop framework (Rust + WebView)
- ✅ React 18 + TypeScript 5.8 - UI framework with strict typing
- ✅ Vite 7.1 - Fast build tool and dev server
- ✅ TailwindCSS 3.4 - Utility-first CSS framework
- ✅ shadcn/ui - High-quality React component library
- ✅ Zustand 5.0 - Lightweight state management with persistence
- ✅ React Router 7.9 - Client-side routing
- ✅ Axios 1.13 - HTTP client with JWT interceptors

**Architecture Components**
- ✅ API Service Layer - Integrated with backend API
- ✅ State Management - Auth & Health slices with localStorage persistence
- ✅ TypeScript Types - Complete type definitions for all models
- ✅ JWT Authentication Flow - Access + refresh token with auto-refresh on 401
- ✅ Tauri Permissions - HTTP requests & file system access configured

### 🔨 To Be Implemented (UI Components)

**Phase 1: Router & Layouts**
- ⏳ React Router configuration with protected routes
- ⏳ AuthLayout for login/register pages
- ⏳ MainLayout with Sidebar + Header
- ⏳ ProtectedRoute component for auth guards

**Phase 2: Authentication**
- ⏳ LoginPage with form validation
- ⏳ RegisterPage with password confirmation
- ⏳ JWT token storage and refresh logic
- ⏳ Toast notifications for errors

**Phase 3: Calendar View**
- ⏳ Monthly calendar grid with navigation
- ⏳ Day cards with color-coded effort scores
- ⏳ Quick preview of daily metrics
- ⏳ Click to open detailed day view

**Phase 4: Day View (7 Sections)**
- ⏳ Meals tracking with macronutrients
- ⏳ Exercise logging with duration/intensity
- ⏳ Water intake with visual progress bar
- ⏳ Sleep tracking with quality rating
- ⏳ Mood tracking with tags
- ⏳ Notes (markdown editor)
- ⏳ AI Summary with effort score

**Phase 5: Statistics**
- ⏳ 7 charts with Recharts (weight, activity, nutrition, water, sleep, mood, effort)
- ⏳ Date range filters (week/month/custom)
- ⏳ Data aggregation and trend analysis

**Phase 6: Profile & Settings**
- ⏳ User profile editing
- ⏳ Goals configuration (water, calories, sleep)
- ⏳ Theme toggle (light/dark mode)
- ⏳ Language selection (EN/RU/CZ)

## 🚀 Quick Start

### Prerequisites

**System Requirements**
- Node.js 20+ and npm 10+
- Rust 1.70+ (for Tauri)
- Linux: webkit2gtk-4.1, libgtk-3-dev, libssl-dev
- Windows: WebView2 (bundled)
- macOS: Xcode Command Line Tools

**Backend API**
- FitCoach backend running on http://localhost:8001
- See [../backend/README.md](../backend/README.md) for setup

### Installation

1. **Install system dependencies (Linux only)**
```bash
# Debian/Ubuntu
sudo apt install libwebkit2gtk-4.1-dev build-essential curl wget file \
  libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev

# Arch Linux
sudo pacman -S webkit2gtk base-devel curl wget file openssl gtk3 \
  libayatana-appindicator librsvg

# Fedora
sudo dnf install webkit2gtk4.1-devel openssl-devel curl wget file \
  gtk3-devel libappindicator-gtk3-devel librsvg2-devel
```

2. **Install Node.js dependencies**
```bash
cd /path/to/fit-coach/desktop
npm install
```

3. **Install Tauri CLI**
```bash
cargo install tauri-cli
# or use npm version
npm install -g @tauri-apps/cli
```

4. **Start development server**
```bash
# Terminal 1: Start backend API
cd ../backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Start desktop app
cd ../desktop
npm run tauri dev
```

5. **Build for production**
```bash
npm run tauri build
```

The built application will be in `src-tauri/target/release/bundle/`

## 📖 Configuration

### Environment Variables

API base URL is configured in `src/services/api/client.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8001/api/v1';
```

For production, update this to your backend URL.

### Tauri Permissions

Configured in `src-tauri/capabilities/default.json`:

```json
{
  "permissions": [
    "core:default",
    "shell:allow-open",
    "http:default",
    "fs:allow-read",
    "fs:allow-write"
  ]
}
```

## 🎨 UI Implementation Plan

### Phase 1: Router & Layouts (~3 hours)

**Files to create:**
```
src/
├── App.tsx                          # Router configuration
├── components/layout/
│   ├── AuthLayout.tsx              # Centered card for auth pages
│   ├── MainLayout.tsx              # Sidebar + Header + Content
│   ├── Sidebar.tsx                 # Navigation menu
│   ├── Header.tsx                  # Top bar with user info
│   └── ProtectedRoute.tsx          # Auth guard HOC
```

**Routes:**
- `/login` → LoginPage (public)
- `/register` → RegisterPage (public)
- `/` → CalendarPage (protected)
- `/day/:id` → DayView (protected)
- `/stats` → StatsPage (protected)
- `/profile` → ProfilePage (protected)

---

### Phase 2: Authentication (~3 hours)

**Files to create:**
```
src/pages/auth/
├── LoginPage.tsx                   # Email + password form
└── RegisterPage.tsx                # Registration form
```

**Features:**
- Form validation with Zod
- Error handling with toast notifications
- JWT token storage in Zustand
- Automatic redirect after login
- "Remember me" functionality

**Integration:**
```typescript
const handleLogin = async (data) => {
  const response = await authService.login(data);
  authStore.setTokens(response.access_token, response.refresh_token);
  authStore.setUser(await userService.getProfile());
  navigate('/');
};
```

---

### Phase 3: Calendar View (~4 hours)

**Files to create:**
```
src/pages/dashboard/
└── CalendarPage.tsx                # Monthly grid + day cards

src/components/day/
└── DayCardPreview.tsx              # Compact day summary
```

**Layout:**
```
┌─────────────────────────────────────────┐
│ November 2025             < Today >     │
├─────────────────────────────────────────┤
│ Mon  Tue  Wed  Thu  Fri  Sat  Sun      │
│ ──────────────────────────────────────  │
│  1    2    3    4    5    6    7       │
│  📝   ✅   ⚠️   📝   ✅   ─    ─       │
│  8    9   10   11   12   13   14       │
│  ✅   📝   ✅   ✅   ─    ─    ─       │
└─────────────────────────────────────────┘
```

**Color coding by effort_score:**
- 🟢 Green (8-10): Excellent day
- 🟡 Yellow (5-7): Good day
- 🟠 Orange (3-4): Needs improvement
- 🔴 Red (0-2): Low effort
- ⚫ Gray: No data

**Features:**
- Previous/next month navigation
- "Today" quick button
- Click day → open /day/:id
- Fetch days with dayService.getDays(startDate, endDate)

---

### Phase 4: Day View (~10 hours)

**Files to create:**
```
src/pages/day/
└── DayView.tsx                     # Main container with tabs

src/components/day/
├── MealsSection.tsx                # Meal list + add form
├── MealForm.tsx                    # Dialog for add/edit meal
├── ExerciseSection.tsx             # Exercise list + add form
├── ExerciseForm.tsx                # Dialog for add/edit exercise
├── WaterSection.tsx                # Progress bar + quick add
├── SleepSection.tsx                # Time pickers + quality
├── MoodSection.tsx                 # 1-5 scale + tags
├── NotesSection.tsx                # Markdown editor
└── AISummarySection.tsx            # AI-generated summary
```

**Tab Structure:**
```
┌──────────────────────────────────────────────┐
│  Wednesday, Nov 13, 2025                     │
│  ┌────┬────┬────┬────┬────┬────┬────────┐  │
│  │Meal│Exer│Wate│Slee│Mood│Note│Summary │  │
│  └────┴────┴────┴────┴────┴────┴────────┘  │
├──────────────────────────────────────────────┤
│                                              │
│  [Active Tab Content]                        │
│                                              │
└──────────────────────────────────────────────┘
```

**4.1 Meals Section**

Display list of meals:
```
Breakfast - 08:00
├─ Oatmeal with berries (450 kcal)
├─ Protein: 25g | Carbs: 60g | Fat: 15g
└─ Notes: "Added honey and walnuts"
    [Edit] [Delete]

[+ Add Meal]
```

Form fields:
- Category: Breakfast/Lunch/Dinner/Snack
- Time picker
- Name (text)
- Calories, Protein, Carbs, Fat (numbers)
- Notes (textarea)

**4.2 Exercise Section**

Display exercises:
```
Morning Run - 07:00
├─ Duration: 45min
├─ Distance: 8km
├─ Intensity: 4/5
└─ Burned: ~400 kcal
    [Edit] [Delete]

[+ Add Exercise]
```

Form fields:
- Type: Running/Gym/Yoga/Swimming/Other
- Duration (time)
- Distance (optional)
- Intensity slider (1-5)
- Heart rate (optional)
- Notes

**4.3 Water Section**

Visual progress:
```
Daily Goal: 2.5L
┌────────────────────────────────┐
│████████████████░░░░░░░░░░░░░░  │ 2.0L / 2.5L (80%)
└────────────────────────────────┘

[+0.25L]  [+0.5L]  [+1.0L]

History:
- 15:30: +0.5L
- 13:00: +0.5L
- 10:00: +0.5L
```

**4.4 Sleep Section**

Form:
```
Bedtime:  [22:30] (time picker)
Wake up:  [06:00] (time picker)

Duration: 7h 30min (auto-calculated)

Quality:  ⭐⭐⭐⭐☆ (4/5)

Notes: "Woke up once at 3am"
```

**4.5 Mood Section**

Display:
```
How was your day?
😢  😕  😐  🙂  😊
1   2   3   4   5

Selected: 4 (🙂)

Tags: [Productive] [Energized] [Focused]
      [Stressed] [Anxious]

Notes: "Great day at work!"
```

**4.6 Notes Section**

Markdown editor:
```
┌──────────────────────────────────┐
│ # My Day                         │
│                                  │
│ Today was productive. Achieved:  │
│ - Finished project milestone     │
│ - Morning workout                │
│ - Healthy meals                  │
│                                  │
└──────────────────────────────────┘
     [Preview]  [Save]
```

**4.7 AI Summary Section**

Display:
```
┌───────────────────────────────────────┐
│  AI Summary                           │
│  ──────────────────────────────────   │
│                                       │
│  Effort Score: 8/10 ⭐⭐⭐⭐          │
│                                       │
│  "Great day! You maintained balanced  │
│  nutrition with 1800 kcal, completed  │
│  2 workouts, and stayed well          │
│  hydrated. Sleep was good at 7.5h.    │
│  Keep up the consistency!"            │
│                                       │
│  💡 Micro-step for tomorrow:          │
│  "Try adding 10min morning stretch"   │
│                                       │
│  [Regenerate Summary]                 │
└───────────────────────────────────────┘
```

Integration:
```typescript
const summary = await aiService.generateSummary(dayId);
```

---

### Phase 5: Statistics (~5 hours)

**Files to create:**
```
src/pages/stats/
└── StatsPage.tsx                   # Container with filters

src/components/stats/
├── WeightChart.tsx                 # Line chart
├── ActivityChart.tsx               # Bar chart
├── NutritionChart.tsx              # Line chart
├── WaterChart.tsx                  # Bar chart
├── SleepChart.tsx                  # Line chart
├── MoodChart.tsx                   # Line chart
└── EffortChart.tsx                 # Line chart
```

**Filters:**
```
[Week] [Month] [Custom Range]
```

**7 Charts with Recharts:**
1. Weight Trend - Line chart (current vs target)
2. Activity Summary - Bar chart (exercise minutes)
3. Nutrition - Line chart (calories vs goal)
4. Hydration - Bar chart (water intake vs goal)
5. Sleep - Line chart (duration vs 7h baseline)
6. Mood Trend - Line chart (average mood)
7. Effort Score - Line chart (AI scores)

**Data fetching:**
```typescript
const days = await dayService.getDays(startDate, endDate);
// Aggregate data for charts
```

---

### Phase 6: Profile & Settings (~2 hours)

**Files to create:**
```
src/pages/profile/
└── ProfilePage.tsx                 # User settings form
```

**Sections:**

**Personal Info:**
```
Full Name: [John Doe]
Age: [30]
Height: [180] cm
Current Weight: [75] kg
Target Weight: [70] kg
```

**Goals:**
```
Daily Water Goal: [2.5] L
Daily Calorie Goal: [2000] kcal
Sleep Goal: [7.5] hours
```

**Settings:**
```
Theme: [Light] [Dark] [System]
Language: [EN] [RU] [CZ]
Notifications: [✓] Daily reminder at 21:00
```

**Actions:**
```
[Save Changes]  [Logout]
```

Integration:
```typescript
await userService.updateProfile(profileData);
authStore.setUser(updatedUser);
```

---

## 📁 Project Structure

```
desktop/
├── src/
│   ├── App.tsx                          # ⏳ Router configuration (TO DO)
│   ├── main.tsx                         # ✅ Entry point
│   ├── index.css                        # ✅ Global styles + Tailwind
│   │
│   ├── components/
│   │   ├── ui/                          # ✅ shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   └── select.tsx
│   │   │
│   │   ├── layout/                      # ⏳ Layout components (TO DO)
│   │   │   ├── AuthLayout.tsx
│   │   │   ├── MainLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   │
│   │   ├── auth/                        # ⏳ Auth components (TO DO)
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   │
│   │   ├── day/                         # ⏳ Day components (TO DO)
│   │   │   ├── DayCardPreview.tsx
│   │   │   ├── MealsSection.tsx
│   │   │   ├── MealForm.tsx
│   │   │   ├── ExerciseSection.tsx
│   │   │   ├── ExerciseForm.tsx
│   │   │   ├── WaterSection.tsx
│   │   │   ├── SleepSection.tsx
│   │   │   ├── MoodSection.tsx
│   │   │   ├── NotesSection.tsx
│   │   │   └── AISummarySection.tsx
│   │   │
│   │   ├── stats/                       # ⏳ Statistics components (TO DO)
│   │   │   ├── WeightChart.tsx
│   │   │   ├── ActivityChart.tsx
│   │   │   ├── NutritionChart.tsx
│   │   │   ├── WaterChart.tsx
│   │   │   ├── SleepChart.tsx
│   │   │   ├── MoodChart.tsx
│   │   │   └── EffortChart.tsx
│   │   │
│   │   └── common/                      # ⏳ Shared components (TO DO)
│   │       ├── Loading.tsx
│   │       ├── ErrorBoundary.tsx
│   │       └── ThemeToggle.tsx
│   │
│   ├── pages/                           # ⏳ Page components (TO DO)
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   └── RegisterPage.tsx
│   │   ├── dashboard/
│   │   │   └── CalendarPage.tsx
│   │   ├── day/
│   │   │   └── DayView.tsx
│   │   ├── stats/
│   │   │   └── StatsPage.tsx
│   │   └── profile/
│   │       └── ProfilePage.tsx
│   │
│   ├── services/                        # API services
│   │   ├── api/
│   │   │   └── client.ts               # ✅ Axios instance with JWT
│   │   └── modules/
│   │       ├── authService.ts          # ✅ Auth API
│   │       ├── dayService.ts           # ✅ Day API
│   │       ├── userService.ts          # ⏳ User API (TO DO)
│   │       ├── mealsService.ts         # ⏳ Meals API (TO DO)
│   │       ├── exercisesService.ts     # ⏳ Exercises API (TO DO)
│   │       ├── waterService.ts         # ⏳ Water API (TO DO)
│   │       ├── sleepService.ts         # ⏳ Sleep API (TO DO)
│   │       ├── moodService.ts          # ⏳ Mood API (TO DO)
│   │       ├── notesService.ts         # ⏳ Notes API (TO DO)
│   │       └── aiService.ts            # ⏳ AI API (TO DO)
│   │
│   ├── store/                           # ✅ Zustand state management
│   │   ├── slices/
│   │   │   ├── authSlice.ts            # ✅ Auth state
│   │   │   └── healthSlice.ts          # ✅ Health data state
│   │   └── index.ts                    # ✅ Combined store
│   │
│   ├── types/                           # ✅ TypeScript types
│   │   ├── api/
│   │   │   └── auth.ts                 # ✅ Auth types
│   │   └── models/
│   │       └── health.ts               # ✅ Health models
│   │
│   ├── utils/                           # ✅ Utilities
│   │   └── date.ts                     # ✅ Date formatting
│   │
│   ├── hooks/                           # ⏳ Custom React hooks (TO DO)
│   │   ├── useAuth.ts
│   │   ├── useDay.ts
│   │   └── useToast.ts
│   │
│   └── constants/                       # ✅ Constants
│       └── api.ts                      # ✅ API constants
│
├── src-tauri/                           # Tauri Rust backend
│   ├── src/
│   │   └── main.rs                     # ✅ Tauri app entry
│   ├── Cargo.toml                      # ✅ Rust dependencies
│   └── tauri.conf.json                 # ✅ Tauri configuration
│
├── package.json                         # ✅ Node.js dependencies
├── tsconfig.json                        # ✅ TypeScript config
├── vite.config.ts                       # ✅ Vite config
├── tailwind.config.js                   # ✅ Tailwind config
├── components.json                      # ✅ shadcn/ui config
└── README.md                            # This file
```

**Legend:**
- ✅ Implemented
- ⏳ To be implemented

## 🛠️ Technology Stack

### Frontend Framework
- **React** 18.3 - UI library
- **TypeScript** 5.8 - Type-safe JavaScript
- **Vite** 7.1 - Build tool and dev server

### Native Desktop
- **Tauri** 2.0 - Rust-based native framework
- **Rust** 1.70+ - Systems programming language

### UI & Styling
- **TailwindCSS** 3.4 - Utility-first CSS
- **shadcn/ui** - Radix UI-based components
- **Lucide React** - Icon library
- **Recharts** 2.3 - Chart library

### State Management
- **Zustand** 5.0 - Lightweight state management
- **Zustand Persist** - localStorage persistence

### Routing & Navigation
- **React Router** 7.9 - Client-side routing

### HTTP & API
- **Axios** 1.13 - HTTP client
- **JWT** - Token-based authentication

### Validation
- **Zod** 4.1 - Schema validation

### Development Tools
- **ESLint** - Linting
- **Prettier** - Code formatting
- **TypeScript ESLint** - TypeScript linting

## 📊 Performance

Target metrics:
- App startup: < 2s
- Route navigation: < 100ms
- API requests: < 500ms (depends on backend)
- Memory usage: < 200MB

## 🔒 Security Features

- **JWT Authentication** - Secure token-based auth
- **Token Refresh** - Automatic on 401 responses
- **HTTPS** - Encrypted API communication (production)
- **Local Storage** - Tokens stored in browser localStorage
- **Input Validation** - Zod schema validation on forms
- **XSS Prevention** - React's built-in escaping

## 🧪 Testing Strategy

### Manual Testing Checklist

**Authentication:**
- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Logout and verify redirect
- [ ] Token auto-refresh on 401

**Protected Routes:**
- [ ] Access protected route while logged out → redirect to /login
- [ ] Access protected route while logged in → show content

**Day View:**
- [ ] Create new day
- [ ] Add meal to day
- [ ] Add exercise to day
- [ ] Add water intake
- [ ] Update sleep record
- [ ] Update mood
- [ ] Add notes
- [ ] Generate AI summary

**CRUD Operations:**
- [ ] Create, read, update, delete for all entities
- [ ] Verify ownership (can't edit other users' data)

**UI/UX:**
- [ ] Dark mode toggle works
- [ ] Responsive design on different window sizes
- [ ] Forms validate correctly
- [ ] Toast notifications show on errors
- [ ] Loading states display properly

### Integration Testing

Future: Add Playwright or Cypress for E2E tests

## 🚀 Deployment

### Building for Production

```bash
# Build optimized bundle
npm run tauri build

# Output locations:
# Linux: src-tauri/target/release/bundle/deb/
# Windows: src-tauri/target/release/bundle/msi/
# macOS: src-tauri/target/release/bundle/dmg/
```

### Distribution

**Linux:**
```bash
# .deb package (Debian/Ubuntu)
sudo dpkg -i fitcoach_0.1.0_amd64.deb

# .AppImage (universal)
chmod +x fitcoach_0.1.0_amd64.AppImage
./fitcoach_0.1.0_amd64.AppImage
```

**Windows:**
```bash
# .msi installer
fitcoach_0.1.0_x64.msi
```

**macOS:**
```bash
# .dmg installer
open fitcoach_0.1.0_universal.dmg
```

### Production Checklist

- [ ] Update API base URL to production backend
- [ ] Enable HTTPS for API calls
- [ ] Remove debug logging
- [ ] Test on target platforms (Linux/Windows/macOS)
- [ ] Code signing (macOS/Windows)
- [ ] Icon assets (multiple sizes)
- [ ] Create GitHub release
- [ ] Write changelog

## 📝 Additional Dependencies Needed

### shadcn/ui Components

Install as needed for UI implementation:

```bash
npx shadcn@latest add tabs
npx shadcn@latest add badge
npx shadcn@latest add progress
npx shadcn@latest add separator
npx shadcn@latest add toast
npx shadcn@latest add slider
npx shadcn@latest add calendar
npx shadcn@latest add avatar
```

Already installed:
- ✅ button, input, card, dialog, dropdown-menu, select

## 🤝 Contributing

1. Create a feature branch from `main`
2. Follow existing code style
3. Use TypeScript strict mode
4. Test manually before submitting PR
5. Update README if adding new features

## 📄 License

MIT License - See [LICENSE](../LICENSE) file

## 📞 Support

For issues and questions:
- See project documentation in `../docs/`
- Check backend API docs: http://localhost:8001/api/docs
- Review backend README: [../backend/README.md](../backend/README.md)

## 🗺️ Roadmap

### ✅ Completed (Phase 0)

- Tauri 2.0 project setup
- React + TypeScript + Vite configuration
- TailwindCSS integration
- shadcn/ui component library
- Zustand state management
- API services (auth, day)
- TypeScript type definitions
- JWT authentication flow
- Axios interceptors

### 🔨 In Progress (Phase 1-2)

- Router configuration
- Layout components (AuthLayout, MainLayout)
- Authentication pages (Login, Register)

### ⏳ Planned (Phase 3-6)

- Calendar view with day cards
- Detailed day view (7 sections)
- Statistics page with charts
- Profile & settings
- Additional service modules
- Error handling & loading states
- Dark mode
- Responsive design

### 🔮 Future Enhancements

- Offline support with SQLite cache
- Desktop notifications
- Export/import data (JSON)
- Keyboard shortcuts
- Advanced markdown editor for notes
- Image upload for meals
- Multi-language support (EN/RU/CZ)
- Accessibility improvements (ARIA)
- Auto-updates via Tauri

---

**Version**: 0.1.0
**Last Updated**: 2025-11-01
**Status**: Foundation Complete, UI Development Ready ✅

---

## 📚 Related Documentation

- [Project Specification](../project.md)
- [App Compatibility](../app_compability.md)
- [Backend README](../backend/README.md)
- [Tauri Documentation](https://tauri.app)
- [React Documentation](https://react.dev)
- [shadcn/ui Documentation](https://ui.shadcn.com)
