# FitCoach Desktop - Architecture Documentation

## Overview
This document describes the foundational architecture implemented for the FitCoach desktop application.

## Technology Stack
- **Framework**: React 19 + TypeScript
- **Desktop**: Tauri v2
- **State Management**: Zustand with persistence
- **HTTP Client**: Axios
- **Date Utilities**: date-fns
- **UI Components**: Radix UI + Tailwind CSS
- **Routing**: React Router DOM v7

## Project Structure

```
src/
├── components/          # React components
│   ├── auth/           # Authentication components
│   ├── charts/         # Chart/visualization components
│   ├── day/            # Day view components
│   ├── health/         # Health tracking components
│   ├── layout/         # Layout components (header, sidebar, etc.)
│   └── ui/             # Shared UI components (Radix UI wrappers)
├── pages/              # Page-level components
│   ├── auth/           # Login, Register pages
│   ├── calendar/       # Calendar view
│   ├── dashboard/      # Main dashboard
│   └── settings/       # Settings page
├── services/           # API and business logic
│   ├── api/
│   │   └── client.ts   # Axios instance with interceptors
│   └── modules/
│       ├── authService.ts    # Authentication API calls
│       └── dayService.ts     # Day management API calls
├── store/              # Zustand state management
│   ├── slices/
│   │   ├── authSlice.ts      # Auth state
│   │   └── healthSlice.ts    # Health data state
│   └── index.ts        # Combined store
├── types/              # TypeScript type definitions
│   ├── api/
│   │   └── auth.ts     # Auth API types
│   └── models/
│       └── health.ts   # Health data models
├── utils/              # Utility functions
│   └── date.ts         # Date formatting utilities
├── hooks/              # Custom React hooks (empty, ready for use)
└── constants/          # App constants
    └── api.ts          # API configuration
```

## Core Components

### 1. Type System

#### Authentication Types (`src/types/api/auth.ts`)
- `LoginRequest`: Email and password for login
- `LoginResponse`: JWT tokens from API
- `RegisterRequest`: User registration data
- `User`: Complete user profile model

#### Health Models (`src/types/models/health.ts`)
- `Day`: Container for all daily health data
- `Meal`: Meal tracking with macros
- `Exercise`: Exercise tracking
- `WaterIntake`: Water consumption tracking
- `SleepRecord`: Sleep duration and quality
- `MoodRecord`: Mood tracking
- `Note`: Daily notes

### 2. API Client (`src/services/api/client.ts`)

**Features:**
- Base URL: `http://localhost:8001/api/v1`
- Automatic JWT token injection via request interceptor
- Automatic token refresh on 401 responses
- Error handling and logout on refresh failure

**Interceptors:**
- **Request**: Adds `Authorization: Bearer {token}` header
- **Response**: Handles 401 errors, refreshes token, retries request

### 3. Service Modules

#### Auth Service (`src/services/modules/authService.ts`)
- `login(data)`: Authenticate user
- `register(data)`: Create new account
- `logout()`: Invalidate session
- `refreshToken(token)`: Get new access token

#### Day Service (`src/services/modules/dayService.ts`)
- `getDays(startDate?, endDate?)`: Fetch days with optional date range
- `getDay(dayId)`: Fetch single day with all data
- `createDay(date)`: Create new day entry
- `deleteDay(dayId)`: Remove day entry

### 4. State Management

#### Auth Slice (`src/store/slices/authSlice.ts`)
**State:**
- `user`: Current user data
- `accessToken`: JWT access token
- `refreshToken`: JWT refresh token
- `isAuthenticated`: Boolean authentication status

**Actions:**
- `setUser(user)`: Set current user
- `setTokens(access, refresh)`: Update tokens
- `logout()`: Clear all auth state

#### Health Slice (`src/store/slices/healthSlice.ts`)
**State:**
- `currentDay`: Currently viewed day
- `days`: Array of loaded days
- `isLoading`: Loading indicator

**Actions:**
- `setCurrentDay(day)`: Set active day
- `setDays(days)`: Update days array
- `setLoading(bool)`: Toggle loading state

#### Store Configuration (`src/store/index.ts`)
- Combined store using Zustand
- Persistence middleware (saves auth tokens to localStorage)
- Custom hooks: `useAuthStore()`, `useHealthStore()`

### 5. Utilities

#### Date Utilities (`src/utils/date.ts`)
- `formatDate(date)`: Format to `yyyy-MM-dd`
- `formatDateTime(date)`: Format to `yyyy-MM-dd HH:mm:ss`

#### Constants (`src/constants/api.ts`)
- `API_BASE_URL`: Backend API endpoint
- `API_TIMEOUT`: Request timeout (30s)

## Tauri Configuration

### HTTP Permissions
API client is allowed to communicate with:
- `http://localhost:8001/*`
- `http://127.0.0.1:8001/*`

### Filesystem Permissions
App can access:
- `$APPDATA/*` - Application data directory
- `$APPCONFIG/*` - Configuration directory
- `$APPDATA/fitcoach-storage` - Persistent storage

### Window Configuration
- Default size: 1200x800
- Minimum size: 800x600
- Title: "FitCoach Desktop"

## Data Flow

### Authentication Flow
1. User submits login form
2. `authService.login()` sends credentials
3. API returns `access_token` and `refresh_token`
4. Store updates with `setTokens()` and `setUser()`
5. Tokens persisted to localStorage
6. All subsequent API calls include token

### Token Refresh Flow
1. API request receives 401 response
2. Interceptor catches error
3. Calls `/auth/refresh` with refresh token
4. Updates access token in store
5. Retries original request with new token
6. If refresh fails, logout user

### Health Data Flow
1. Component calls `dayService.getDay(id)`
2. API client adds auth headers
3. Response mapped to `Day` type
4. Store updated with `setCurrentDay(day)`
5. UI re-renders with new data

## Usage Examples

### Login Example
```typescript
import { authService } from '@/services';
import { useAuthStore } from '@/store';

const { setUser, setTokens } = useAuthStore();

const handleLogin = async (email: string, password: string) => {
  const response = await authService.login({ email, password });
  setTokens(response.access_token, response.refresh_token);

  // Fetch user profile
  const user = await authService.getProfile();
  setUser(user);
};
```

### Fetch Day Data Example
```typescript
import { dayService } from '@/services';
import { useHealthStore } from '@/store';

const { setCurrentDay, setLoading } = useHealthStore();

const loadDay = async (dayId: number) => {
  setLoading(true);
  try {
    const day = await dayService.getDay(dayId);
    setCurrentDay(day);
  } finally {
    setLoading(false);
  }
};
```

### Using Store in Components
```typescript
import { useAuthStore, useHealthStore } from '@/store';

function Dashboard() {
  const { user, isAuthenticated } = useAuthStore();
  const { currentDay, isLoading } = useHealthStore();

  if (!isAuthenticated) return <Login />;
  if (isLoading) return <Spinner />;

  return (
    <div>
      <h1>Welcome, {user?.full_name}</h1>
      {currentDay && <DayView day={currentDay} />}
    </div>
  );
}
```

## Next Steps

### Components to Build
1. **Authentication**
   - Login form
   - Registration form
   - Protected route wrapper

2. **Layout**
   - Main navigation
   - Sidebar
   - Header with user menu

3. **Health Tracking**
   - Meal entry form
   - Exercise tracker
   - Water intake widget
   - Sleep/mood trackers

4. **Visualization**
   - Progress charts (recharts)
   - Calendar view
   - Statistics dashboard

### Services to Add
- `mealService.ts` - CRUD for meals
- `exerciseService.ts` - CRUD for exercises
- `waterService.ts` - Water intake tracking
- `sleepService.ts` - Sleep tracking
- `moodService.ts` - Mood tracking
- `userService.ts` - User profile management

### Hooks to Create
- `useAuth.ts` - Authentication logic
- `useDay.ts` - Day management
- `useApi.ts` - Generic API calls with loading/error states

## Build and Development

### Development
```bash
npm run dev
npm run tauri dev
```

### Build
```bash
npm run build
npm run tauri build
```

### Type Check
```bash
npx tsc --noEmit
```

## File Statistics
- Total TypeScript files created: 17
- Total lines of code: ~314
- All files compile without errors
- All types properly defined
