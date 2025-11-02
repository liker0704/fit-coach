# FitCoach Desktop - Component Documentation

**Status**: 🔨 In Development
**Framework**: Electron + React 19 + TypeScript 5.8

This document provides comprehensive documentation for all React components in the FitCoach desktop application.

---

## 📁 Project Structure

```
desktop/src/
├── components/          # React components
│   ├── auth/           # Authentication components
│   ├── charts/         # Chart-related components
│   ├── common/         # Shared/reusable components
│   ├── day/            # Day view components
│   ├── error/          # Error handling components
│   ├── health/         # Health tracking components
│   ├── layout/         # Layout components (Header, Sidebar)
│   ├── stats/          # Statistics charts
│   ├── theme/          # Theme provider
│   └── ui/             # shadcn/ui base components
├── pages/              # Page components
│   ├── auth/           # Login, Register
│   ├── calendar/       # Calendar view, Day detail
│   ├── dashboard/      # Statistics dashboard
│   └── settings/       # Profile, Settings
├── hooks/              # Custom React hooks
├── services/           # API service layer
├── store/              # Zustand state management
├── types/              # TypeScript type definitions
└── utils/              # Utility functions
```

---

## 🎨 UI Component Library

FitCoach uses [shadcn/ui](https://ui.shadcn.com/) - a collection of re-usable components built with Radix UI and TailwindCSS.

### Core UI Components

Located in: `src/components/ui/`

| Component | File | Description | Props |
|-----------|------|-------------|-------|
| **Button** | `button.tsx` | Primary action button | `variant`, `size`, `disabled`, `onClick` |
| **Input** | `input.tsx` | Text input field | `type`, `placeholder`, `value`, `onChange` |
| **Card** | `card.tsx` | Content container | `className`, `children` |
| **Dialog** | `dialog.tsx` | Modal dialog | `open`, `onOpenChange`, `title`, `children` |
| **Select** | `select.tsx` | Dropdown selector | `value`, `onValueChange`, `options` |
| **Tabs** | `tabs.tsx` | Tabbed interface | `defaultValue`, `tabs[]` |
| **Checkbox** | `checkbox.tsx` | Checkbox input | `checked`, `onCheckedChange`, `label` |
| **Label** | `label.tsx` | Form label | `htmlFor`, `children` |
| **Textarea** | `textarea.tsx` | Multi-line text input | `value`, `onChange`, `rows` |
| **Badge** | `badge.tsx` | Status badge | `variant`, `children` |
| **Progress** | `progress.tsx` | Progress bar | `value`, `max` |
| **Slider** | `slider.tsx` | Numeric slider | `value`, `onValueChange`, `min`, `max` |
| **Separator** | `separator.tsx` | Horizontal/vertical divider | `orientation` |
| **Toast** | `toast.tsx` + `toaster.tsx` | Notification system | `title`, `description`, `variant` |
| **AlertDialog** | `alert-dialog.tsx` | Confirmation dialog | `open`, `onConfirm`, `title`, `description` |
| **DropdownMenu** | `dropdown-menu.tsx` | Dropdown menu | `trigger`, `items[]` |
| **LoadingSpinner** | `loading-spinner.tsx` | Loading indicator | `size`, `className` |

### Custom UI Components

| Component | File | Description |
|-----------|------|-------------|
| **TimePicker24** | `TimePicker24.tsx` | 24-hour time picker with validation |
| **DeleteConfirmDialog** | `DeleteConfirmDialog.tsx` | Reusable delete confirmation dialog |

---

## 🔐 Authentication Components

Located in: `src/components/auth/` and `src/pages/auth/`

### LoginPage
**File**: `src/pages/auth/LoginPage.tsx`
**Route**: `/login`

**Description**: User login page with email/password authentication.

**Features**:
- Email and password input fields
- Form validation (email format, required fields)
- JWT token handling (access + refresh tokens)
- Error display with toast notifications
- Redirect to dashboard on success
- Link to registration page

**State Management**: Uses `authSlice` from Zustand store

**API**: `POST /api/v1/auth/login`

---

### RegisterPage
**File**: `src/pages/auth/RegisterPage.tsx`
**Route**: `/register`

**Description**: User registration page.

**Features**:
- Email, username, password, password confirmation inputs
- Client-side validation
- Password strength requirements
- Auto-login after successful registration
- Link to login page

**API**: `POST /api/v1/auth/register`

---

## 📅 Calendar Components

Located in: `src/pages/calendar/`

### CalendarPage
**File**: `src/pages/calendar/CalendarPage.tsx`
**Route**: `/calendar`

**Description**: Monthly calendar view showing all days with quick previews.

**Features**:
- Monthly grid calendar
- Navigate between months (prev/next buttons)
- Day cards with color-coded effort scores
- Click on day to open detailed view
- Quick preview of daily metrics (meals, exercises, water)
- Highlight today's date

**Components Used**:
- `DayCardPreview` - Individual day card in grid

**State**: Fetches days from `healthSlice` store

---

### DayView
**File**: `src/pages/calendar/DayView.tsx`
**Route**: `/calendar/:date`

**Description**: Detailed view for a specific day with all health tracking sections.

**Features**:
- 7 main sections (Meals, Exercises, Water, Sleep, Mood, Notes, AI Summary)
- Tabbed interface for easy navigation
- Add/edit/delete functionality for each section
- Real-time updates with optimistic UI
- Date navigation (previous/next day)

**Sections**:
1. **Meals** - `MealsSection`
2. **Exercises** - `ExerciseSection`
3. **Water** - `WaterSection`
4. **Sleep** - `SleepSection`
5. **Mood** - `MoodSection`
6. **Notes** - `NotesSection`
7. **AI Summary** - `AISummarySection`

---

## 🍽️ Day View Components

Located in: `src/components/day/`

### MealsSection
**File**: `src/components/day/MealsSection.tsx`

**Description**: Displays and manages meals for the day.

**Features**:
- List of meals grouped by category (Breakfast, Lunch, Dinner, Snack)
- Add new meal button
- Edit existing meals
- Delete meals with confirmation
- Display calories and macronutrients
- Calculate daily totals

**Subcomponents**:
- `MealForm` - Form for adding/editing meals

---

### MealForm
**File**: `src/components/day/MealForm.tsx`

**Description**: Form dialog for creating/editing a meal.

**Fields**:
- Meal name (text)
- Category (select: Breakfast, Lunch, Dinner, Snack)
- Quantity (number with unit)
- Calories (number)
- Protein (g)
- Carbs (g)
- Fats (g)
- Description (textarea)

**Validation**:
- Name is required
- Category is required
- Quantity must be positive
- Macronutrients must be non-negative

**API**:
- Create: `POST /api/v1/meals`
- Update: `PUT /api/v1/meals/{id}`

---

### ExerciseSection
**File**: `src/components/day/ExerciseSection.tsx`

**Description**: Displays and manages exercises for the day.

**Features**:
- List of exercises with type icons
- Add new exercise button
- Edit existing exercises
- Delete exercises with confirmation
- Display duration, distance (if running), intensity

**Subcomponents**:
- `ExerciseForm` - Form for adding/editing exercises

---

### ExerciseForm
**File**: `src/components/day/ExerciseForm.tsx`

**Description**: Form dialog for creating/editing an exercise.

**Fields**:
- Exercise type (select: Running, Gym, Yoga, Cycling, Walking, Other)
- Duration (minutes)
- Distance (km, optional - shown for Running/Cycling)
- Intensity (select: Low, Medium, High)
- Heart rate (BPM, optional)
- Calories burned (auto-calculated or manual)
- Notes (textarea)

**API**:
- Create: `POST /api/v1/exercises`
- Update: `PUT /api/v1/exercises/{id}`

---

### WaterSection
**File**: `src/components/day/WaterSection.tsx`

**Description**: Visual water intake tracker with progress bar.

**Features**:
- Visual water glasses representation
- Progress bar showing daily goal (2.5-3L)
- Quick add buttons (250ml, 500ml, 1000ml)
- Custom amount dialog
- Total intake display
- History of water intake entries

**Subcomponents**:
- `WaterAddDialog` - Dialog for adding custom water amount

**API**:
- Create: `POST /api/v1/water`

---

### SleepSection
**File**: `src/components/day/SleepSection.tsx`

**Description**: Sleep tracking with quality rating.

**Features**:
- Sleep start/end time pickers (24-hour format)
- Auto-calculated duration
- Quality rating (1-5 stars)
- Notes about sleep
- Display hours and minutes

**Subcomponents**:
- `SleepForm` - Form for adding/editing sleep

**API**:
- Create: `POST /api/v1/sleep`
- Update: `PUT /api/v1/sleep/{id}`

---

### MoodSection
**File**: `src/components/day/MoodSection.tsx`

**Description**: Mood tracking with tags and notes.

**Features**:
- Mood rating (1-5 scale with emoji)
- Tags (Stress, Focus, Energy, Anxiety, Happy, Calm)
- Multi-select tags
- Notes textarea
- Visual mood display

**Subcomponents**:
- `MoodForm` - Form for adding/editing mood

**API**:
- Create: `POST /api/v1/mood`
- Update: `PUT /api/v1/mood/{id}`

---

### NotesSection
**File**: `src/components/day/NotesSection.tsx`

**Description**: Daily notes with markdown support (planned).

**Features**:
- Textarea for free-form notes
- Auto-save on blur
- Character count
- Markdown formatting (future)

**Subcomponents**:
- `NotesForm` - Form for editing notes

**API**:
- Create: `POST /api/v1/notes`
- Update: `PUT /api/v1/notes/{id}`

---

### AISummarySection
**File**: `src/components/day/AISummarySection.tsx`

**Description**: AI-generated daily summary and effort score.

**Features**:
- "Generate Summary" button
- Loading state during generation
- Display AI summary text
- Effort score (0-10) with visual representation
- Regenerate functionality
- Cache summary in database

**Status**: 📋 Planned (LLM integration pending)

**API**: `POST /api/v1/ai/summary/{day_id}` (not yet implemented)

---

### DayCardPreview
**File**: `src/components/day/DayCardPreview.tsx`

**Description**: Compact day card for calendar grid view.

**Features**:
- Date display
- Effort score badge
- Quick metrics (meals count, exercises count, water %)
- Color-coded border based on effort score
- Click to open detailed day view
- Empty state for days without data

**Props**:
```typescript
interface DayCardPreviewProps {
  date: string;
  dayData?: Day;
  onClick: () => void;
}
```

---

## 📊 Statistics Components

Located in: `src/components/stats/` and `src/pages/dashboard/`

### StatsPage
**File**: `src/pages/dashboard/StatsPage.tsx`
**Route**: `/stats`

**Description**: Dashboard with 7 health charts and trend analysis.

**Features**:
- Date range selector (last 7/30/90 days, custom range)
- 7 chart cards in grid layout
- Lazy loading for performance optimization
- Export data (future feature)

**Charts**:
1. **WeightChart** - Weight over time
2. **ActivityChart** - Exercise minutes per day
3. **NutritionChart** - Calories and macronutrients
4. **WaterChart** - Water intake vs. goal
5. **SleepChart** - Sleep duration and quality
6. **MoodChart** - Average mood score
7. **EffortChart** - Daily effort scores

---

### WeightChart
**File**: `src/components/stats/WeightChart.tsx`

**Description**: Line chart showing weight trend over time.

**Library**: Recharts `LineChart`

**Features**:
- Weight on Y-axis, Date on X-axis
- Trend line
- Hover tooltip with exact values
- Goal line (if set)

---

### ActivityChart
**File**: `src/components/stats/ActivityChart.tsx`

**Description**: Bar chart showing exercise minutes per day.

**Features**:
- Exercise minutes on Y-axis
- Grouped by exercise type (Running, Gym, Yoga, etc.)
- Stacked bars for multiple exercises per day
- Color-coded by type

---

### NutritionChart
**File**: `src/components/stats/NutritionChart.tsx`

**Description**: Multi-line chart for calories and macros.

**Features**:
- 4 lines: Calories, Protein, Carbs, Fats
- Toggle lines on/off
- Goal lines for each metric
- Hover tooltip with all values

---

### WaterChart
**File**: `src/components/stats/WaterChart.tsx`

**Description**: Bar chart for daily water intake.

**Features**:
- Water intake (ml) on Y-axis
- Goal line at 2500ml
- Color changes (red/yellow/green) based on goal achievement

---

### SleepChart
**File**: `src/components/stats/SleepChart.tsx`

**Description**: Combined chart for sleep duration and quality.

**Features**:
- Bar for sleep hours
- Line for quality rating (1-5)
- Recommended sleep range (7-9 hours) highlighted

---

### MoodChart
**File**: `src/components/stats/MoodChart.tsx`

**Description**: Line chart for mood trends.

**Features**:
- Average mood score (1-5) on Y-axis
- Emoji indicators
- Smooth curve

---

### EffortChart
**File**: `src/components/stats/EffortChart.tsx`

**Description**: Line/area chart for daily effort scores.

**Features**:
- Effort score (0-10) on Y-axis
- Area fill for visual emphasis
- Average line

---

## 🏗️ Layout Components

Located in: `src/components/layout/`

### MainLayout
**File**: `src/components/layout/MainLayout.tsx`

**Description**: Main application layout with sidebar and header.

**Structure**:
```
┌─────────────────────────────────┐
│          Header                 │
├─────────┬───────────────────────┤
│ Sidebar │     Content Area      │
│         │                       │
│         │                       │
└─────────┴───────────────────────┘
```

**Features**:
- Persistent sidebar with navigation
- Header with user info and logout
- Content area for page rendering

---

### Sidebar
**File**: `src/components/layout/Sidebar.tsx`

**Description**: Navigation sidebar with menu items.

**Menu Items**:
- 📅 Calendar (`/calendar`)
- 📊 Statistics (`/stats`)
- ⚙️ Settings (`/settings`)
- 🚪 Logout

**Features**:
- Active route highlighting
- Icons for each menu item
- Collapsible (future feature)

---

### Header
**File**: `src/components/layout/Header.tsx`

**Description**: Top header bar with user info.

**Features**:
- App title/logo
- Current date display
- User email/username
- Theme toggle (future)
- Notifications (future)

---

### AuthLayout
**File**: `src/components/layout/AuthLayout.tsx`

**Description**: Layout for authentication pages (Login/Register).

**Features**:
- Centered content
- App branding
- No sidebar/header
- Background image/gradient

---

### ProtectedRoute
**File**: `src/components/layout/ProtectedRoute.tsx`

**Description**: Route guard component for authenticated routes.

**Logic**:
```typescript
if (!isAuthenticated) {
  return <Navigate to="/login" />;
}
return <Outlet />;
```

**Usage**:
```tsx
<Route element={<ProtectedRoute />}>
  <Route path="/calendar" element={<CalendarPage />} />
  <Route path="/stats" element={<StatsPage />} />
  ...
</Route>
```

---

## 🔧 Utility Components

### ErrorBoundary
**File**: `src/components/error/ErrorBoundary.tsx`

**Description**: React error boundary for graceful error handling.

**Features**:
- Catch React component errors
- Display error message to user
- Log errors to console
- Provide "Reload" button

---

### LazyLoadChart
**File**: `src/components/common/LazyLoadChart.tsx`

**Description**: Wrapper for lazy loading chart components.

**Purpose**: Improve performance by loading charts only when visible.

**Usage**:
```tsx
<LazyLoadChart>
  <WeightChart data={weightData} />
</LazyLoadChart>
```

---

### ThemeProvider
**File**: `src/components/theme/ThemeProvider.tsx`

**Description**: Context provider for theme management.

**Features**:
- Light/dark mode toggle
- Persist theme preference in localStorage
- Apply theme class to document root

---

## 🪝 Custom Hooks

Located in: `src/hooks/`

### useToast
**File**: `src/hooks/use-toast.ts`

**Description**: Hook for displaying toast notifications.

**Usage**:
```typescript
const { toast } = useToast();

toast({
  title: "Success",
  description: "Day created successfully",
  variant: "success"
});
```

---

### useContainerSize
**File**: `src/hooks/useContainerSize.tsx`

**Description**: Hook for responsive chart sizing.

**Returns**: `{ width, height }` of container element.

**Usage**:
```typescript
const { width, height } = useContainerSize(containerRef);
```

---

### useScrollRedirect
**File**: `src/hooks/useScrollRedirect.ts`

**Description**: Hook to redirect to top of page on route change.

---

## 📦 State Management

FitCoach uses **Zustand** for lightweight, fast state management.

### Store Structure

Located in: `src/store/slices/`

#### authSlice
**File**: `src/store/slices/authSlice.ts`

**State**:
```typescript
{
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
}
```

**Actions**:
- `login(tokens, user)` - Set auth state
- `logout()` - Clear auth state
- `updateUser(user)` - Update user info
- `setTokens(access, refresh)` - Update tokens

**Persistence**: localStorage via Zustand persist middleware

---

#### healthSlice
**File**: `src/store/slices/healthSlice.ts`

**State**:
```typescript
{
  days: Day[];
  currentDay: Day | null;
  loading: boolean;
  error: string | null;
}
```

**Actions**:
- `fetchDays(startDate, endDate)` - Fetch days in range
- `fetchDay(date)` - Fetch specific day
- `createDay(data)` - Create new day
- `updateDay(id, data)` - Update day
- `deleteDay(id)` - Delete day

---

#### themeSlice
**File**: `src/store/slices/themeSlice.ts`

**State**:
```typescript
{
  theme: 'light' | 'dark';
}
```

**Actions**:
- `setTheme(theme)` - Set theme
- `toggleTheme()` - Switch between light/dark

---

## 🔌 API Services

Located in: `src/services/modules/`

All API services use Axios with JWT interceptors for authentication.

### Service Files

| Service | File | Endpoints |
|---------|------|-----------|
| **Auth** | `authService.ts` | `/auth/login`, `/auth/register`, `/auth/refresh` |
| **Days** | `dayService.ts` | CRUD for `/days` |
| **Meals** | `mealsService.ts` | CRUD for `/meals` |
| **Exercises** | `exercisesService.ts` | CRUD for `/exercises` |
| **Water** | `waterService.ts` | CRUD for `/water` |
| **Sleep** | `sleepService.ts` | CRUD for `/sleep` |
| **Mood** | `moodService.ts` | CRUD for `/mood` |
| **Notes** | `notesService.ts` | CRUD for `/notes` |
| **AI** | `aiService.ts` | `/ai/summary`, `/ai/insights` (planned) |
| **User** | `userService.ts` | `/users/me`, update profile |

---

## 🎯 Best Practices

### Component Guidelines

1. **Functional Components**: Use functional components with hooks
2. **TypeScript**: All components must have proper type definitions
3. **Props Interface**: Define props interface for each component
4. **Single Responsibility**: One component = one responsibility
5. **Composition**: Build complex UIs by composing smaller components
6. **Error Handling**: Use ErrorBoundary for critical components

### File Naming

- **Components**: PascalCase (e.g., `MealForm.tsx`)
- **Hooks**: camelCase with `use` prefix (e.g., `useToast.ts`)
- **Utilities**: camelCase (e.g., `date.ts`)
- **Services**: camelCase (e.g., `authService.ts`)

### Component Structure

```tsx
// 1. Imports
import React from 'react';
import { Button } from '@/components/ui/button';

// 2. Type definitions
interface MyComponentProps {
  title: string;
  onSave: () => void;
}

// 3. Component
export const MyComponent: React.FC<MyComponentProps> = ({ title, onSave }) => {
  // 4. Hooks
  const [value, setValue] = React.useState('');

  // 5. Event handlers
  const handleClick = () => {
    console.log('clicked');
  };

  // 6. Render
  return (
    <div>
      <h1>{title}</h1>
      <Button onClick={handleClick}>Save</Button>
    </div>
  );
};
```

---

## 🚧 Future Components (Planned)

- [ ] **SettingsPage** - User profile and app settings
- [ ] **GoalsPage** - Set and track health goals
- [ ] **ExportDialog** - Export data to JSON/CSV
- [ ] **ImportDialog** - Import data from file
- [ ] **NotificationsPanel** - In-app notifications
- [ ] **AchievementsPage** - Gamification badges
- [ ] **DarkModeToggle** - Theme switcher in header

---

## 📚 Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Recharts Documentation](https://recharts.org/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)

---

**Last Updated**: 2025-11-02
**Status**: Living Document - Update as components are added/modified
