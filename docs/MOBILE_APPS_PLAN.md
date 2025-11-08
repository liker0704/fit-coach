# Mobile Apps Development Plan

## Overview

Comprehensive architecture and implementation plan for iOS and Android native mobile applications for the FitCoach health tracking system.

**Status:** 📋 Planning Phase
**Target Platforms:** iOS 15+ | Android 8.0+ (API 26+)
**Approach:** React Native (Cross-Platform) **OR** Native Development
**Backend:** Existing FastAPI REST API with JWT authentication

---

## 🎯 Project Goals

### Primary Objectives

1. **Feature Parity** - Implement all core features from Desktop app
2. **Native Performance** - 60 FPS animations, smooth scrolling, instant response
3. **Offline Support** - Local data caching with sync mechanism
4. **Battery Efficiency** - Optimized for mobile device constraints
5. **Push Notifications** - Daily reminders and coaching insights
6. **Platform Integration** - HealthKit (iOS) / Google Fit (Android)

### Success Metrics

- App size: < 50 MB
- Launch time: < 2 seconds
- API response time: < 500ms
- Offline mode: Full read access, queue writes
- Battery drain: < 3% per hour of active use

---

## 🔀 Technology Stack Decision

### Option A: React Native (Cross-Platform) ✅ RECOMMENDED

**Pros:**
- ✅ Single codebase for iOS + Android (80% code reuse)
- ✅ TypeScript + React (same as Desktop)
- ✅ Faster development (6-8 weeks vs 12-16 weeks)
- ✅ Shared API service layer with Desktop
- ✅ Rich ecosystem (Expo, React Navigation, React Native Paper)
- ✅ Hot reload for rapid iteration

**Cons:**
- ❌ Bridge overhead (minor performance impact)
- ❌ Larger app size than native (~40-50 MB)
- ❌ Some platform-specific features need native modules

**Stack:**
```json
{
  "framework": "React Native 0.73+",
  "language": "TypeScript 5.8",
  "navigation": "React Navigation 6",
  "ui": "React Native Paper / NativeBase",
  "state": "Zustand 5.0",
  "storage": "AsyncStorage + WatermelonDB",
  "api": "Axios",
  "charts": "react-native-chart-kit / Victory Native",
  "notifications": "expo-notifications",
  "auth": "expo-secure-store"
}
```

### Option B: Native Development (iOS + Android Separate)

**Pros:**
- ✅ Best performance and platform integration
- ✅ Smallest app size (~15-20 MB per platform)
- ✅ Full access to platform APIs
- ✅ Better debugging tools

**Cons:**
- ❌ Double development effort (12-16 weeks)
- ❌ Two separate codebases to maintain
- ❌ Different languages (Swift vs Kotlin)
- ❌ Duplicate business logic

**iOS Stack:**
```swift
{
  "language": "Swift 5.9",
  "ui": "SwiftUI",
  "networking": "URLSession + Alamofire",
  "storage": "CoreData + GRDB",
  "charts": "Swift Charts",
  "notifications": "UserNotifications",
  "health": "HealthKit"
}
```

**Android Stack:**
```kotlin
{
  "language": "Kotlin 1.9",
  "ui": "Jetpack Compose",
  "networking": "Retrofit + OkHttp",
  "storage": "Room Database",
  "charts": "MPAndroidChart / Vico",
  "notifications": "WorkManager",
  "health": "Google Fit API"
}
```

### 📊 Comparison Matrix

| Feature | React Native | Native (iOS + Android) |
|---------|-------------|------------------------|
| Development Time | 6-8 weeks | 12-16 weeks |
| Code Reuse | 80% | 0% |
| Performance | 95% native | 100% native |
| App Size | ~45 MB | ~18 MB each |
| Maintenance | Single codebase | Two codebases |
| Developer Skill | React/TypeScript | Swift + Kotlin |
| Platform APIs | Via modules | Direct access |
| **Recommendation** | ✅ **Start here** | Use for v2.0 if needed |

---

## 🏗️ Architecture (React Native)

### High-Level Architecture

```
┌─────────────────────────────────────────┐
│         React Native App (iOS/Android)  │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ React UI     │  │ Native Modules  │ │
│  │ (TypeScript) │←→│ (Swift/Kotlin)  │ │
│  └──────┬───────┘  └────────┬────────┘ │
│         │                    │          │
│  ┌──────▼────────────────────▼──────┐  │
│  │    JavaScript Bridge (JSI)       │  │
│  └──────┬──────────────────┬────────┘  │
└─────────┼──────────────────┼───────────┘
          │                  │
    ┌─────▼─────┐      ┌────▼─────┐
    │ AsyncStore│      │HealthKit │
    │ WatermelonDB│      │Google Fit│
    └─────┬─────┘      └──────────┘
          │
    ┌─────▼──────────────────────────┐
    │   FastAPI Backend (Existing)   │
    │   - JWT Authentication         │
    │   - REST API Endpoints         │
    │   - AI Agents                  │
    └────────────────────────────────┘
```

### Layer Breakdown

#### 1. Presentation Layer (React Native)

**Screens:**
- `AuthStack` - Login, Register, ForgotPassword
- `MainTabs` - Calendar, Day, Stats, AI, Profile
- `DayTabs` - Overview, Meals, Exercise, Water, Sleep, Mood, Notes
- `AIStack` - Chatbot, Coaches, Summary, Vision

**Components:**
```typescript
src/
├── screens/
│   ├── auth/
│   │   ├── LoginScreen.tsx
│   │   └── RegisterScreen.tsx
│   ├── calendar/
│   │   ├── CalendarScreen.tsx
│   │   └── DayScreen.tsx
│   ├── stats/
│   │   └── StatisticsScreen.tsx
│   └── profile/
│       └── ProfileScreen.tsx
├── components/
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Card.tsx
│   ├── day/
│   │   ├── MealCard.tsx
│   │   ├── ExerciseCard.tsx
│   │   └── WaterProgress.tsx
│   └── charts/
│       ├── WeightChart.tsx
│       └── CaloriesChart.tsx
└── navigation/
    ├── AppNavigator.tsx
    ├── AuthNavigator.tsx
    └── MainTabNavigator.tsx
```

#### 2. Business Logic Layer

**State Management (Zustand):**
```typescript
src/store/
├── authStore.ts          // Authentication state
├── dayStore.ts           // Current day data
├── statsStore.ts         // Statistics cache
├── syncStore.ts          // Offline sync queue
└── settingsStore.ts      // App settings
```

**Services:**
```typescript
src/services/
├── api/
│   ├── apiClient.ts      // Axios instance with interceptors
│   ├── authService.ts    // Login, register, refresh token
│   ├── dayService.ts     // CRUD for days
│   ├── mealService.ts    // Meal operations
│   └── agentService.ts   // AI agent calls
├── storage/
│   ├── secureStorage.ts  // JWT tokens (expo-secure-store)
│   ├── asyncStorage.ts   // User preferences
│   └── database.ts       // WatermelonDB for offline data
├── sync/
│   └── syncEngine.ts     // Sync local ↔ remote
└── notifications/
    └── notificationService.ts  // Push notifications
```

#### 3. Data Layer

**Local Database (WatermelonDB):**
```typescript
src/database/
├── schema.ts             // SQLite schema
├── models/
│   ├── DayModel.ts
│   ├── MealModel.ts
│   ├── ExerciseModel.ts
│   └── UserModel.ts
└── migrations/
    └── 001_initial.ts
```

**Why WatermelonDB?**
- Fast (lazy loading, optimized queries)
- Offline-first architecture
- React hooks integration
- Sync with REST APIs

#### 4. Platform-Specific Modules

**iOS Native (Swift):**
```swift
ios/FitCoach/
├── HealthKitModule.swift     // Export workouts/weight to HealthKit
├── NotificationModule.swift  // Local notifications
└── BiometricsModule.swift    // FaceID/TouchID
```

**Android Native (Kotlin):**
```kotlin
android/app/src/main/java/com/fitcoach/
├── GoogleFitModule.kt        // Sync with Google Fit
├── NotificationModule.kt     // Android notifications
└── BiometricsModule.kt       // Fingerprint auth
```

---

## 📱 Feature Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)

**Tasks:**

1. **Project Setup**
   - [ ] Initialize React Native project with TypeScript
   - [ ] Configure Expo (or React Native CLI)
   - [ ] Setup folder structure
   - [ ] Install dependencies (navigation, UI library, Zustand, Axios)
   - [ ] Configure TypeScript strict mode
   - [ ] Setup ESLint + Prettier

2. **API Integration**
   - [ ] Create API client with Axios
   - [ ] Implement JWT interceptor (refresh token flow)
   - [ ] Create service layer (auth, day, meal, exercise)
   - [ ] Test API calls with existing backend

3. **Authentication**
   - [ ] Design Login/Register screens
   - [ ] Implement auth flow (login → store JWT → navigate)
   - [ ] Secure storage for tokens (expo-secure-store)
   - [ ] Auto-login on app launch
   - [ ] Logout functionality

4. **Navigation**
   - [ ] Setup React Navigation 6
   - [ ] Auth stack (Login, Register)
   - [ ] Main tab navigator (Calendar, Day, Stats, AI, Profile)
   - [ ] Deep linking configuration

**Deliverable:** Working authentication + navigation skeleton

---

### Phase 2: Calendar & Day View (Week 3-4)

**Tasks:**

1. **Calendar Screen**
   - [ ] Month view with react-native-calendars
   - [ ] Mark days with data (dots/colors)
   - [ ] Day selection → navigate to DayScreen
   - [ ] Current day highlighting
   - [ ] Month navigation (prev/next)

2. **Day Screen - Overview Tab**
   - [ ] Day header (date, tag, feeling, effort score)
   - [ ] Weight input with auto-save
   - [ ] Quick stats summary (calories, water, sleep)
   - [ ] AI Summary section (fetch from backend)

3. **Day Screen - Tabs Implementation**
   - [ ] Tab navigator for 7 sections
   - [ ] Meals tab - List meals, add/edit/delete
   - [ ] Exercise tab - List workouts, add/edit/delete
   - [ ] Water tab - Visual progress bar, add intake
   - [ ] Sleep tab - Duration slider, quality rating
   - [ ] Mood tab - Mood scale 1-5, tags
   - [ ] Notes tab - Markdown editor

4. **CRUD Operations**
   - [ ] Add meal modal (name, calories, protein, carbs, fats)
   - [ ] Add exercise modal (name, duration, intensity)
   - [ ] Delete confirmations
   - [ ] Optimistic UI updates

**Deliverable:** Full day tracking functionality

---

### Phase 3: Statistics & Charts (Week 5)

**Tasks:**

1. **Statistics Screen**
   - [ ] Date range picker (week/month/year)
   - [ ] Weight chart (line chart)
   - [ ] Calories chart (bar chart)
   - [ ] Water intake chart (area chart)
   - [ ] Sleep duration chart (line chart)
   - [ ] Exercise distance chart (bar chart)

2. **Chart Implementation**
   - [ ] Install react-native-chart-kit or Victory Native
   - [ ] Create reusable chart components
   - [ ] Handle empty states
   - [ ] Loading skeletons
   - [ ] Tooltips on data points

3. **Data Aggregation**
   - [ ] Calculate weekly/monthly averages
   - [ ] Group data by date range
   - [ ] Cache statistics in Zustand store

**Deliverable:** Full statistics page with visualizations

---

### Phase 4: AI Agents (Week 6)

**Tasks:**

1. **Chatbot Screen**
   - [ ] Chat UI with message bubbles
   - [ ] Text input with send button
   - [ ] Message history display
   - [ ] Loading indicator for AI response
   - [ ] Error handling (network issues)

2. **Vision Agent**
   - [ ] Camera/Photo picker integration
   - [ ] Image upload to backend
   - [ ] Display recognized meal data
   - [ ] Save meal from photo

3. **Coach Dialogs**
   - [ ] Nutrition Coach modal
   - [ ] Workout Coach modal
   - [ ] Context-aware suggestions (pass user data)

4. **Daily Summary**
   - [ ] Fetch daily summary from backend
   - [ ] Display on Day Overview tab
   - [ ] Refresh on pull-down

**Deliverable:** All 5 AI agents functional on mobile

---

### Phase 5: Offline Support & Sync (Week 7)

**Tasks:**

1. **Local Database Setup**
   - [ ] Install WatermelonDB
   - [ ] Define database schema (Day, Meal, Exercise, etc.)
   - [ ] Create database models
   - [ ] Setup migrations

2. **Offline Mode**
   - [ ] Cache API responses in local DB
   - [ ] Read from local DB when offline
   - [ ] Queue write operations (add/edit/delete)
   - [ ] Show offline indicator in UI

3. **Sync Engine**
   - [ ] Detect network connectivity
   - [ ] Sync local → remote when online
   - [ ] Handle conflicts (last-write-wins)
   - [ ] Sync on app launch and periodically

4. **Testing Offline Mode**
   - [ ] Test airplane mode
   - [ ] Test poor network conditions
   - [ ] Verify sync after reconnection

**Deliverable:** Full offline functionality

---

### Phase 6: Notifications & Settings (Week 8)

**Tasks:**

1. **Push Notifications**
   - [ ] Install expo-notifications
   - [ ] Request notification permissions
   - [ ] Schedule daily reminder (local notification)
   - [ ] Handle notification tap (deep link to app)

2. **Profile & Settings**
   - [ ] Profile form (name, age, height, weight goals)
   - [ ] Settings (language, theme, notifications)
   - [ ] Language switcher (i18n with i18next)
   - [ ] Logout button

3. **Platform Integration (Optional)**
   - [ ] iOS: Export weight to HealthKit
   - [ ] Android: Sync with Google Fit
   - [ ] Request health permissions

4. **Polish & Testing**
   - [ ] Test on iOS simulator + real device
   - [ ] Test on Android emulator + real device
   - [ ] Fix UI bugs (safe area, keyboard handling)
   - [ ] Optimize performance (reduce re-renders)

**Deliverable:** Production-ready mobile apps

---

## 📂 Project Structure

### Complete Folder Structure

```
mobile/
├── ios/                          # iOS native code (auto-generated)
├── android/                      # Android native code (auto-generated)
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── EmptyState.tsx
│   │   ├── day/
│   │   │   ├── MealCard.tsx
│   │   │   ├── ExerciseCard.tsx
│   │   │   ├── WaterProgress.tsx
│   │   │   ├── SleepSlider.tsx
│   │   │   └── MoodScale.tsx
│   │   ├── charts/
│   │   │   ├── WeightChart.tsx
│   │   │   ├── CaloriesChart.tsx
│   │   │   └── WaterChart.tsx
│   │   └── ai/
│   │       ├── ChatMessage.tsx
│   │       ├── CoachDialog.tsx
│   │       └── SummaryCard.tsx
│   ├── screens/
│   │   ├── auth/
│   │   │   ├── LoginScreen.tsx
│   │   │   ├── RegisterScreen.tsx
│   │   │   └── ForgotPasswordScreen.tsx
│   │   ├── calendar/
│   │   │   ├── CalendarScreen.tsx
│   │   │   └── DayScreen.tsx
│   │   ├── stats/
│   │   │   └── StatisticsScreen.tsx
│   │   ├── ai/
│   │   │   ├── ChatbotScreen.tsx
│   │   │   └── VisionScreen.tsx
│   │   └── profile/
│   │       ├── ProfileScreen.tsx
│   │       └── SettingsScreen.tsx
│   ├── navigation/
│   │   ├── AppNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   ├── MainTabNavigator.tsx
│   │   └── DayTabNavigator.tsx
│   ├── services/
│   │   ├── api/
│   │   │   ├── apiClient.ts
│   │   │   ├── authService.ts
│   │   │   ├── dayService.ts
│   │   │   ├── mealService.ts
│   │   │   ├── exerciseService.ts
│   │   │   └── agentService.ts
│   │   ├── storage/
│   │   │   ├── secureStorage.ts
│   │   │   ├── asyncStorage.ts
│   │   │   └── database.ts
│   │   ├── sync/
│   │   │   └── syncEngine.ts
│   │   └── notifications/
│   │       └── notificationService.ts
│   ├── store/
│   │   ├── authStore.ts
│   │   ├── dayStore.ts
│   │   ├── statsStore.ts
│   │   ├── syncStore.ts
│   │   └── settingsStore.ts
│   ├── database/
│   │   ├── schema.ts
│   │   ├── models/
│   │   │   ├── DayModel.ts
│   │   │   ├── MealModel.ts
│   │   │   └── ExerciseModel.ts
│   │   └── migrations/
│   │       └── 001_initial.ts
│   ├── types/
│   │   ├── models/
│   │   │   ├── User.ts
│   │   │   ├── Day.ts
│   │   │   ├── Meal.ts
│   │   │   └── Exercise.ts
│   │   └── api/
│   │       └── responses.ts
│   ├── i18n/
│   │   ├── config.ts
│   │   └── locales/
│   │       ├── en.json
│   │       ├── ru.json
│   │       └── cz.json
│   ├── theme/
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   └── spacing.ts
│   ├── utils/
│   │   ├── dateHelpers.ts
│   │   ├── validators.ts
│   │   └── formatters.ts
│   └── App.tsx
├── assets/
│   ├── images/
│   ├── fonts/
│   └── icons/
├── app.json
├── package.json
├── tsconfig.json
├── babel.config.js
└── README.md
```

---

## 🔐 Security Considerations

### Authentication

1. **JWT Storage**
   - Store access token in memory (not AsyncStorage)
   - Store refresh token in SecureStore (iOS Keychain / Android Keystore)
   - Auto-refresh token before expiry

2. **Biometric Auth**
   - Optional FaceID/TouchID/Fingerprint login
   - Fallback to password
   - SecureStore for biometric credentials

### Data Security

1. **Local Database Encryption**
   - Encrypt WatermelonDB with SQLCipher
   - Use user password as encryption key

2. **API Communication**
   - HTTPS only (enforce TLS 1.2+)
   - Certificate pinning (optional for production)
   - No sensitive data in URLs (use POST body)

### Permissions

- Request only necessary permissions
- Explain permission usage in prompts
- Graceful degradation if denied

---

## 🧪 Testing Strategy

### Unit Tests
- Zustand stores
- Helper functions (date formatting, validators)
- API service mocks

### Integration Tests
- Login flow → API → store → navigation
- Add meal → save to DB → sync to backend
- Offline mode → queue operations → sync when online

### E2E Tests (Detox)
- Full user journeys (login → add meal → view stats)
- Test on real devices (iOS + Android)

### Manual Testing Checklist
- [ ] Test on iOS 15, 16, 17
- [ ] Test on Android 8, 10, 13
- [ ] Test on various screen sizes (iPhone SE, Pro Max, tablets)
- [ ] Test offline mode (airplane mode)
- [ ] Test poor network (throttle to 3G)
- [ ] Battery drain test (use app for 1 hour)
- [ ] Accessibility (VoiceOver, TalkBack)

---

## 📦 Deployment

### iOS App Store

**Requirements:**
- Apple Developer Account ($99/year)
- App Store Connect setup
- App icons (1024x1024 + all sizes)
- Screenshots (5.5", 6.5", 12.9")
- Privacy policy URL
- App description + keywords

**Build Process:**
```bash
# 1. Build release version
cd mobile
eas build --platform ios --profile production

# 2. Test with TestFlight
eas submit --platform ios --latest

# 3. Submit for App Store review
# Via App Store Connect dashboard
```

### Google Play Store

**Requirements:**
- Google Play Developer Account ($25 one-time)
- Play Console setup
- App icons (512x512)
- Screenshots (phone + tablet)
- Privacy policy URL
- Content rating questionnaire

**Build Process:**
```bash
# 1. Build release AAB
eas build --platform android --profile production

# 2. Upload to Play Console
eas submit --platform android --latest

# 3. Submit for review
# Via Play Console dashboard
```

---

## 📊 Development Timeline

### Estimated Timeline (React Native)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 1**: Infrastructure | 2 weeks | Auth + Navigation |
| **Phase 2**: Calendar & Day | 2 weeks | Full day tracking |
| **Phase 3**: Statistics | 1 week | Charts + analytics |
| **Phase 4**: AI Agents | 1 week | All 5 agents |
| **Phase 5**: Offline Support | 1 week | Sync engine |
| **Phase 6**: Polish | 1 week | Production ready |
| **Total** | **8 weeks** | MVP on App Stores |

### Team Requirements

**Minimum Team:**
- 1 React Native developer (full-time)
- 1 Backend developer (part-time, for API adjustments)
- 1 UI/UX designer (part-time, for mobile screens)

**Ideal Team:**
- 2 React Native developers
- 1 Backend developer
- 1 UI/UX designer
- 1 QA engineer

---

## 💰 Cost Estimation

### Development Costs (React Native)

| Item | Cost (USD) |
|------|------------|
| React Native Developer (8 weeks × $5k/week) | $40,000 |
| UI/UX Designer (4 weeks × $3k/week) | $12,000 |
| QA Engineer (2 weeks × $2k/week) | $4,000 |
| **Total Development** | **$56,000** |

### Platform Costs (Annual)

| Item | Cost (USD) |
|------|------------|
| Apple Developer Account | $99 |
| Google Play Developer Account | $25 (one-time) |
| Push Notification Service (Firebase) | Free (up to 1M users) |
| **Total Annual** | **$99-$124** |

---

## 🎨 UI/UX Considerations

### Design Principles

1. **Mobile-First**
   - Thumb-friendly tap targets (44x44 pt minimum)
   - Bottom navigation for one-handed use
   - Swipe gestures (swipe to delete, pull to refresh)

2. **Performance**
   - Lazy load lists (FlatList with virtualization)
   - Image optimization (WebP format, caching)
   - Avoid unnecessary re-renders (React.memo, useMemo)

3. **Platform Conventions**
   - iOS: Native-looking buttons, bottom sheets
   - Android: Material Design, FABs, snackbars
   - Share common components but respect platform UX

### Key Screens Design

**Calendar Screen:**
- Month grid with colored dots for logged days
- Swipe left/right for prev/next month
- Tap day → navigate to DayScreen

**Day Screen:**
- Horizontal scrollable tabs at top
- Large tap targets for adding data
- Floating action button (FAB) for quick add

**Stats Screen:**
- Scrollable list of charts
- Date range picker at top
- Each chart collapsible

---

## 🔄 Backend API Adjustments

### Required Changes

**1. Pagination for Lists**
```python
# Add to /days, /meals, /exercises endpoints
@router.get("/days")
async def get_days(
    skip: int = 0,
    limit: int = 50,  # Mobile: fetch 50 at a time
    user_id: int = Depends(get_current_user)
):
    # Return paginated results
```

**2. Batch Operations**
```python
# Add endpoint for batch sync
@router.post("/sync")
async def batch_sync(
    operations: List[SyncOperation],
    user_id: int = Depends(get_current_user)
):
    # Process create/update/delete in one request
```

**3. Image Optimization**
```python
# Resize images before storing
# Return thumbnail URLs for mobile
```

**4. Push Notification Tokens**
```python
# Add FCM/APNS token to User model
class User(Base):
    fcm_token: str  # Firebase Cloud Messaging
    apns_token: str  # Apple Push Notification Service
```

---

## 🚀 Getting Started (React Native)

### Step 1: Initialize Project

```bash
# Create new Expo project with TypeScript
npx create-expo-app mobile --template expo-template-blank-typescript

cd mobile
npm install
```

### Step 2: Install Dependencies

```bash
# Navigation
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context

# UI Components
npm install react-native-paper
npm install react-native-vector-icons

# State Management
npm install zustand

# API & Storage
npm install axios
npm install @react-native-async-storage/async-storage
npm install expo-secure-store

# Database (Offline)
npm install @nozbe/watermelondb @nozbe/with-observables

# Charts
npm install react-native-chart-kit react-native-svg

# Calendar
npm install react-native-calendars

# i18n
npm install i18next react-i18next

# Notifications
npm install expo-notifications

# Camera (for Vision Agent)
npm install expo-camera expo-image-picker
```

### Step 3: Setup Folder Structure

```bash
mkdir -p src/{components,screens,navigation,services,store,database,types,i18n,theme,utils}
mkdir -p src/components/{common,day,charts,ai}
mkdir -p src/screens/{auth,calendar,stats,ai,profile}
mkdir -p src/services/{api,storage,sync,notifications}
mkdir -p src/database/{models,migrations}
mkdir -p src/types/{models,api}
mkdir -p src/i18n/locales
```

### Step 4: Copy Types from Desktop

```bash
# Reuse TypeScript types from desktop app
cp -r ../desktop/src/types/models/* src/types/models/
```

### Step 5: Run Dev Server

```bash
# Start Expo dev server
npm start

# Press 'i' for iOS simulator
# Press 'a' for Android emulator
```

---

## 📚 Learning Resources

### React Native
- [Official Docs](https://reactnative.dev/docs/getting-started)
- [React Navigation](https://reactnavigation.org/docs/getting-started)
- [Expo Docs](https://docs.expo.dev/)

### WatermelonDB
- [Offline-First Guide](https://nozbe.github.io/WatermelonDB/)
- [React Hooks](https://nozbe.github.io/WatermelonDB/Installation.html)

### Platform Integration
- [HealthKit (iOS)](https://developer.apple.com/documentation/healthkit)
- [Google Fit (Android)](https://developers.google.com/fit)

---

## 🎯 Next Steps

### Immediate Actions

1. **Choose Technology Stack**
   - ✅ **Recommended:** React Native for faster MVP
   - Review team skills and timeline
   - Get stakeholder buy-in

2. **Create New Branch**
   ```bash
   git checkout -b feature/mobile-app
   ```

3. **Initialize React Native Project**
   ```bash
   npx create-expo-app mobile --template expo-template-blank-typescript
   ```

4. **Setup Development Environment**
   - Install Xcode (for iOS development)
   - Install Android Studio (for Android development)
   - Configure simulators/emulators

5. **Start Phase 1 (Week 1-2)**
   - Follow tasks in "Phase 1: Core Infrastructure"
   - Setup API integration
   - Implement authentication

---

## 📝 Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-08 | React Native over Native | 80% code reuse, faster to market (8 weeks vs 16) |
| TBD | Expo vs React Native CLI | TBD based on native module requirements |
| TBD | WatermelonDB vs SQLite | TBD based on sync complexity |

---

## 🔗 Related Documentation

- [Desktop App Documentation](../desktop/README.md)
- [Backend API Documentation](../backend/README.md)
- [AI Agents Documentation](../AI_AGENTS_COMPLETE.md)
- [Database Schema](./database-schema.md)

---

**Last Updated:** 2025-11-08
**Status:** 📋 Planning Complete - Ready for Development
**Estimated Completion:** 8 weeks from start date
**Budget:** ~$56,000 (React Native) or ~$112,000 (Native)
