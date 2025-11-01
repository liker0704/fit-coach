# Desktop Client Tasks - Tauri + React детализация

## Обзор
120+ атомарных задач для создания десктопного приложения на Tauri + React + TypeScript.
Каждая задача включает код примеры, компоненты и интеграции.

---

## СЕКЦИЯ 1: Инициализация проекта (10 задач)

### DT-001: Создать Tauri проект
**Время**: 1ч
**Команды**:
```bash
cd desktop
npm create tauri-app@latest . -- --template react-ts
```

**Структура**:
```
desktop/
├── src/           # React app
├── src-tauri/     # Rust backend
│   ├── src/
│   │   └── main.rs
│   ├── Cargo.toml
│   └── tauri.conf.json
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### DT-002: Настроить React + Vite
**Файл vite.config.ts**:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@services': path.resolve(__dirname, './src/services'),
      '@stores': path.resolve(__dirname, './src/stores'),
      '@types': path.resolve(__dirname, './src/types'),
      '@utils': path.resolve(__dirname, './src/utils'),
    },
  },
  server: {
    port: 3000,
  },
})
```

### DT-003: Установить зависимости
**Файл package.json**:
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tauri-apps/api": "^1.5.0",
    "zustand": "^4.4.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "date-fns": "^2.30.0",
    "recharts": "^2.10.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.0",
    "lucide-react": "^0.300.0",
    "react-markdown": "^9.0.0",
    "react-hot-toast": "^2.4.0",
    "framer-motion": "^10.16.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "@typescript-eslint/eslint-plugin": "^6.15.0",
    "@typescript-eslint/parser": "^6.15.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0"
  }
}
```

### DT-004: Настроить Tailwind CSS
**Файл tailwind.config.js**:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        secondary: {
          50: '#f8fafc',
          500: '#64748b',
          600: '#475569',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
    },
  },
  plugins: [],
}
```

### DT-005: Настроить shadcn/ui
**Команды установки**:
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card dialog form input label select toast
```

**Файл components.json**:
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

---

## СЕКЦИЯ 2: Компоненты UI (40 задач)

### DT-011: Layout компонент
**Файл src/components/Layout/Layout.tsx**:
```typescript
import { FC, ReactNode } from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { cn } from '@/lib/utils'

interface LayoutProps {
  children: ReactNode
  className?: string
}

export const Layout: FC<LayoutProps> = ({ children, className }) => {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className={cn(
          "flex-1 overflow-y-auto p-6",
          className
        )}>
          {children}
        </main>
      </div>
    </div>
  )
}
```

### DT-012: Sidebar компонент
**Файл src/components/Layout/Sidebar.tsx**:
```typescript
import { FC, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Calendar,
  Home,
  TrendingUp,
  Target,
  Settings,
  User,
  Menu,
  X
} from 'lucide-react'
import { cn } from '@/lib/utils'

const menuItems = [
  { path: '/', label: 'Dashboard', icon: Home },
  { path: '/calendar', label: 'Calendar', icon: Calendar },
  { path: '/statistics', label: 'Statistics', icon: TrendingUp },
  { path: '/goals', label: 'Goals', icon: Target },
  { path: '/profile', label: 'Profile', icon: User },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export const Sidebar: FC = () => {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()

  return (
    <aside className={cn(
      "bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300",
      collapsed ? "w-16" : "w-64"
    )}>
      <div className="flex items-center justify-between p-4">
        {!collapsed && (
          <h1 className="text-xl font-bold text-primary-600">FitCoach</h1>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
        >
          {collapsed ? <Menu size={20} /> : <X size={20} />}
        </button>
      </div>

      <nav className="mt-8">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path

          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center px-4 py-3 text-sm font-medium transition-colors",
                "hover:bg-gray-100 dark:hover:bg-gray-700",
                isActive && "bg-primary-50 dark:bg-primary-900/20 text-primary-600 border-r-2 border-primary-600",
                !isActive && "text-gray-600 dark:text-gray-300"
              )}
            >
              <Icon size={20} />
              {!collapsed && (
                <span className="ml-3">{item.label}</span>
              )}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
```

### DT-013: Calendar компонент
**Файл src/components/Calendar/Calendar.tsx**:
```typescript
import { FC, useState } from 'react'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday } from 'date-fns'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useNavigate } from 'react-router-dom'
import { useDays } from '@/hooks/useDays'

export const Calendar: FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date())
  const navigate = useNavigate()
  const { days, isLoading } = useDays(currentDate)

  const monthStart = startOfMonth(currentDate)
  const monthEnd = endOfMonth(currentDate)
  const monthDays = eachDayOfInterval({ start: monthStart, end: monthEnd })

  const getEffortColor = (score: number) => {
    if (score >= 8) return 'bg-green-500'
    if (score >= 6) return 'bg-yellow-500'
    if (score >= 4) return 'bg-orange-500'
    return 'bg-red-500'
  }

  const handleDayClick = (date: Date) => {
    navigate(`/day/${format(date, 'yyyy-MM-dd')}`)
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">
          {format(currentDate, 'MMMM yyyy')}
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() - 1))}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <ChevronLeft size={20} />
          </button>
          <button
            onClick={() => setCurrentDate(new Date())}
            className="px-3 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            Today
          </button>
          <button
            onClick={() => setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() + 1))}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-1">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="text-center text-xs font-medium text-gray-500 py-2">
            {day}
          </div>
        ))}

        {monthDays.map((day, index) => {
          const dayData = days?.find(d => d.date === format(day, 'yyyy-MM-dd'))
          const hasData = !!dayData

          return (
            <button
              key={index}
              onClick={() => handleDayClick(day)}
              className={cn(
                "relative aspect-square p-2 border rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors",
                isToday(day) && "ring-2 ring-primary-500",
                !isSameMonth(day, currentDate) && "opacity-50"
              )}
            >
              <span className={cn(
                "text-sm",
                isToday(day) && "font-bold"
              )}>
                {format(day, 'd')}
              </span>

              {hasData && dayData.effortScore && (
                <div className={cn(
                  "absolute bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full",
                  getEffortColor(dayData.effortScore)
                )} />
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
```

### DT-014: DayCard компонент
**Файл src/components/Day/DayCard.tsx**:
```typescript
import { FC, useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { MealSection } from './MealSection'
import { ExerciseSection } from './ExerciseSection'
import { WaterSection } from './WaterSection'
import { SleepSection } from './SleepSection'
import { MoodSection } from './MoodSection'
import { NotesSection } from './NotesSection'
import { SummarySection } from './SummarySection'
import { Day } from '@/types/models'

interface DayCardProps {
  day: Day
  onUpdate: (updates: Partial<Day>) => void
}

export const DayCard: FC<DayCardProps> = ({ day, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('meals')

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">
              {format(new Date(day.date), 'EEEE, MMMM d, yyyy')}
            </h2>
            {day.tag && (
              <span className="inline-block mt-2 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                {day.tag}
              </span>
            )}
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Effort Score</div>
            <div className="text-3xl font-bold text-primary-600">
              {day.effortScore?.toFixed(1) || '-'}
            </div>
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="p-6">
        <TabsList className="grid grid-cols-7 w-full">
          <TabsTrigger value="meals">Meals</TabsTrigger>
          <TabsTrigger value="exercise">Exercise</TabsTrigger>
          <TabsTrigger value="water">Water</TabsTrigger>
          <TabsTrigger value="sleep">Sleep</TabsTrigger>
          <TabsTrigger value="mood">Mood</TabsTrigger>
          <TabsTrigger value="notes">Notes</TabsTrigger>
          <TabsTrigger value="summary">Summary</TabsTrigger>
        </TabsList>

        <TabsContent value="meals">
          <MealSection day={day} onUpdate={onUpdate} />
        </TabsContent>

        <TabsContent value="exercise">
          <ExerciseSection day={day} onUpdate={onUpdate} />
        </TabsContent>

        <TabsContent value="water">
          <WaterSection day={day} onUpdate={onUpdate} />
        </TabsContent>

        <TabsContent value="sleep">
          <SleepSection day={day} onUpdate={onUpdate} />
        </TabsContent>

        <TabsContent value="mood">
          <MoodSection day={day} onUpdate={onUpdate} />
        </TabsContent>

        <TabsContent value="notes">
          <NotesSection day={day} onUpdate={onUpdate} />
        </TabsContent>

        <TabsContent value="summary">
          <SummarySection day={day} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

---

## СЕКЦИЯ 3: State Management (20 задач)

### DT-071: Auth Store
**Файл src/stores/authStore.ts**:
```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authService } from '@/services/auth'
import { User, TokenResponse } from '@/types/auth'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean

  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshAuth: () => Promise<void>
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email, password) => {
        set({ isLoading: true })
        try {
          const response = await authService.login(email, password)

          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
          })

          // Get user info
          const user = await authService.getCurrentUser()
          set({ user })
        } catch (error) {
          set({
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            user: null
          })
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      register: async (data) => {
        set({ isLoading: true })
        try {
          const user = await authService.register(data)
          // Auto login after registration
          await get().login(data.email, data.password)
        } finally {
          set({ isLoading: false })
        }
      },

      logout: async () => {
        const refreshToken = get().refreshToken
        if (refreshToken) {
          try {
            await authService.logout(refreshToken)
          } catch (error) {
            console.error('Logout error:', error)
          }
        }

        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },

      refreshAuth: async () => {
        const refreshToken = get().refreshToken
        if (!refreshToken) {
          throw new Error('No refresh token')
        }

        try {
          const response = await authService.refreshToken(refreshToken)
          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
          })
        } catch (error) {
          // Refresh failed, logout
          get().logout()
          throw error
        }
      },

      setUser: (user) => set({ user }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
```

### DT-072: Day Store
**Файл src/stores/dayStore.ts**:
```typescript
import { create } from 'zustand'
import { dayService } from '@/services/days'
import { Day, Meal, Exercise } from '@/types/models'

interface DayState {
  currentDay: Day | null
  days: Day[]
  isLoading: boolean
  error: string | null

  loadDay: (date: string) => Promise<void>
  loadDays: (startDate?: string, endDate?: string) => Promise<void>
  updateDay: (date: string, updates: Partial<Day>) => Promise<void>

  addMeal: (date: string, meal: Meal) => Promise<void>
  updateMeal: (mealId: number, updates: Partial<Meal>) => Promise<void>
  deleteMeal: (mealId: number) => Promise<void>

  addExercise: (date: string, exercise: Exercise) => Promise<void>
  updateExercise: (exerciseId: number, updates: Partial<Exercise>) => Promise<void>
  deleteExercise: (exerciseId: number) => Promise<void>

  addWater: (date: string, amount: number) => Promise<void>
  generateSummary: (date: string) => Promise<void>
}

export const useDayStore = create<DayState>((set, get) => ({
  currentDay: null,
  days: [],
  isLoading: false,
  error: null,

  loadDay: async (date) => {
    set({ isLoading: true, error: null })
    try {
      const day = await dayService.getDay(date)
      set({ currentDay: day })
    } catch (error) {
      set({ error: error.message })
    } finally {
      set({ isLoading: false })
    }
  },

  loadDays: async (startDate, endDate) => {
    set({ isLoading: true, error: null })
    try {
      const days = await dayService.getDays({ startDate, endDate })
      set({ days })
    } catch (error) {
      set({ error: error.message })
    } finally {
      set({ isLoading: false })
    }
  },

  updateDay: async (date, updates) => {
    try {
      const updatedDay = await dayService.updateDay(date, updates)
      set((state) => ({
        currentDay: state.currentDay?.date === date ? updatedDay : state.currentDay,
        days: state.days.map(d => d.date === date ? updatedDay : d)
      }))
    } catch (error) {
      set({ error: error.message })
    }
  },

  addMeal: async (date, meal) => {
    try {
      const newMeal = await dayService.addMeal(date, meal)
      set((state) => ({
        currentDay: state.currentDay?.date === date
          ? { ...state.currentDay, meals: [...state.currentDay.meals, newMeal] }
          : state.currentDay
      }))
    } catch (error) {
      set({ error: error.message })
    }
  },

  // ... остальные методы
}))
```

---

## СЕКЦИЯ 4: Services и API (10 задач)

### DT-091: API Client
**Файл src/services/api.ts**:
```typescript
import axios, { AxiosInstance, AxiosError } from 'axios'
import { useAuthStore } from '@/stores/authStore'
import toast from 'react-hot-toast'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

class ApiClient {
  private instance: AxiosInstance

  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        const token = useAuthStore.getState().accessToken
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.instance.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            await useAuthStore.getState().refreshAuth()
            const token = useAuthStore.getState().accessToken
            originalRequest.headers.Authorization = `Bearer ${token}`
            return this.instance(originalRequest)
          } catch (refreshError) {
            useAuthStore.getState().logout()
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }

        // Show error toast
        if (error.response?.data?.detail) {
          toast.error(error.response.data.detail)
        } else if (error.message) {
          toast.error(error.message)
        }

        return Promise.reject(error)
      }
    )
  }

  get<T>(url: string, params?: any) {
    return this.instance.get<T>(url, { params })
  }

  post<T>(url: string, data?: any) {
    return this.instance.post<T>(url, data)
  }

  put<T>(url: string, data?: any) {
    return this.instance.put<T>(url, data)
  }

  delete<T>(url: string) {
    return this.instance.delete<T>(url)
  }
}

export const apiClient = new ApiClient()
```

### DT-092: Tauri SQLite Integration
**Файл src/services/cache.ts**:
```typescript
import { invoke } from '@tauri-apps/api/tauri'
import { Day, Meal, Exercise } from '@/types/models'

interface CacheDB {
  execute: (query: string, params?: any[]) => Promise<any>
  select: <T>(query: string, params?: any[]) => Promise<T[]>
  insert: (table: string, data: Record<string, any>) => Promise<number>
  update: (table: string, data: Record<string, any>, where: Record<string, any>) => Promise<void>
  delete: (table: string, where: Record<string, any>) => Promise<void>
}

class CacheService {
  private initialized = false

  async initialize() {
    if (this.initialized) return

    await invoke('init_database')
    await this.createTables()
    this.initialized = true
  }

  private async createTables() {
    const queries = [
      `CREATE TABLE IF NOT EXISTS days (
        id INTEGER PRIMARY KEY,
        date TEXT UNIQUE NOT NULL,
        tag TEXT,
        feeling INTEGER,
        effort_score REAL,
        summary TEXT,
        synced BOOLEAN DEFAULT FALSE,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )`,

      `CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY,
        day_date TEXT NOT NULL,
        category TEXT NOT NULL,
        calories REAL,
        protein REAL,
        carbs REAL,
        fat REAL,
        items TEXT,
        synced BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (day_date) REFERENCES days(date)
      )`,

      `CREATE TABLE IF NOT EXISTS sync_queue (
        id INTEGER PRIMARY KEY,
        entity_type TEXT NOT NULL,
        entity_id INTEGER NOT NULL,
        operation TEXT NOT NULL,
        data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )`
    ]

    for (const query of queries) {
      await invoke('execute_sql', { query })
    }
  }

  async saveDay(day: Day) {
    await this.initialize()

    const existing = await invoke<Day[]>('select_sql', {
      query: 'SELECT * FROM days WHERE date = ?',
      params: [day.date]
    })

    if (existing.length > 0) {
      await invoke('execute_sql', {
        query: `UPDATE days SET tag = ?, feeling = ?, effort_score = ?, summary = ?, synced = ?, updated_at = CURRENT_TIMESTAMP
                WHERE date = ?`,
        params: [day.tag, day.feeling, day.effortScore, day.summary, true, day.date]
      })
    } else {
      await invoke('execute_sql', {
        query: `INSERT INTO days (date, tag, feeling, effort_score, summary, synced)
                VALUES (?, ?, ?, ?, ?, ?)`,
        params: [day.date, day.tag, day.feeling, day.effortScore, day.summary, true]
      })
    }
  }

  async getDay(date: string): Promise<Day | null> {
    await this.initialize()

    const results = await invoke<Day[]>('select_sql', {
      query: 'SELECT * FROM days WHERE date = ?',
      params: [date]
    })

    if (results.length === 0) return null

    const day = results[0]

    // Load related data
    const meals = await invoke<Meal[]>('select_sql', {
      query: 'SELECT * FROM meals WHERE day_date = ?',
      params: [date]
    })

    return {
      ...day,
      meals: meals.map(m => ({
        ...m,
        items: JSON.parse(m.items || '[]')
      }))
    }
  }

  async getPendingSyncItems() {
    await this.initialize()

    return invoke<any[]>('select_sql', {
      query: 'SELECT * FROM sync_queue ORDER BY created_at ASC',
      params: []
    })
  }

  async addToSyncQueue(entityType: string, entityId: number, operation: string, data: any) {
    await this.initialize()

    await invoke('execute_sql', {
      query: `INSERT INTO sync_queue (entity_type, entity_id, operation, data)
              VALUES (?, ?, ?, ?)`,
      params: [entityType, entityId, operation, JSON.stringify(data)]
    })
  }
}

export const cacheService = new CacheService()
```

---

## СЕКЦИЯ 5: Hooks (20 задач)

### DT-075: useAuth Hook
**Файл src/hooks/useAuth.ts**:
```typescript
import { useAuthStore } from '@/stores/authStore'
import { useNavigate } from 'react-router-dom'
import { useCallback } from 'react'

export const useAuth = () => {
  const navigate = useNavigate()
  const {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
  } = useAuthStore()

  const handleLogin = useCallback(async (email: string, password: string) => {
    try {
      await login(email, password)
      navigate('/')
    } catch (error) {
      throw error
    }
  }, [login, navigate])

  const handleLogout = useCallback(async () => {
    await logout()
    navigate('/login')
  }, [logout, navigate])

  return {
    user,
    isAuthenticated,
    isLoading,
    login: handleLogin,
    register,
    logout: handleLogout,
  }
}
```

### DT-076: useDay Hook with React Query
**Файл src/hooks/useDay.ts**:
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { dayService } from '@/services/days'
import { Day } from '@/types/models'
import toast from 'react-hot-toast'

export const useDay = (date: string) => {
  const queryClient = useQueryClient()

  const { data: day, isLoading, error } = useQuery({
    queryKey: ['day', date],
    queryFn: () => dayService.getDay(date),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const updateMutation = useMutation({
    mutationFn: (updates: Partial<Day>) => dayService.updateDay(date, updates),
    onSuccess: () => {
      queryClient.invalidateQueries(['day', date])
      toast.success('Day updated')
    },
    onError: (error) => {
      toast.error('Failed to update day')
    },
  })

  return {
    day,
    isLoading,
    error,
    updateDay: updateMutation.mutate,
    isUpdating: updateMutation.isLoading,
  }
}

export const useDays = (startDate?: string, endDate?: string) => {
  const { data: days, isLoading, error } = useQuery({
    queryKey: ['days', startDate, endDate],
    queryFn: () => dayService.getDays({ startDate, endDate }),
    staleTime: 5 * 60 * 1000,
  })

  return { days, isLoading, error }
}
```

---

## Итоговые метрики Desktop

- **Количество компонентов**: 50+
- **Количество hooks**: 20
- **Количество сервисов**: 10
- **Строк кода**: ~8000
- **Тестовое покрытие**: 70%+
- **Bundle size**: <500KB
- **Время реализации**: ~120 часов

Каждая задача включает:
1. Полный путь к файлу
2. Код компонента/функции
3. TypeScript типы
4. Интеграция с API
5. Стейт менеджмент
6. Тестовые сценарии