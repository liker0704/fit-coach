# FitCoach Mobile App

React Native mobile application for FitCoach health tracking system.

## 📱 Platform Support

- **iOS**: 15.0+
- **Android**: 8.0+ (API 26+)
- **Development**: Expo Go (iOS & Android)

## 🏗️ Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | React Native (Expo) | 0.73+ |
| Language | TypeScript | 5.8 |
| Navigation | React Navigation 6 | 6.x |
| UI Components | React Native Paper | Latest |
| State Management | Zustand | 5.0 |
| HTTP Client | Axios | Latest |
| Storage | Expo SecureStore | Latest |
| Icons | MaterialCommunityIcons | Expo vector-icons |

## 📂 Project Structure

```
mobile/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── common/        # Common components (Button, Input, Card)
│   │   ├── day/           # Day tracking components
│   │   ├── charts/        # Chart components
│   │   └── ai/            # AI agent components
│   ├── screens/           # Screen components
│   │   ├── auth/          # Login, Register
│   │   ├── calendar/      # Calendar view
│   │   ├── stats/         # Statistics
│   │   ├── ai/            # AI agents
│   │   └── profile/       # User profile
│   ├── navigation/        # Navigation setup
│   │   ├── AppNavigator.tsx       # Root navigator
│   │   ├── AuthNavigator.tsx      # Auth stack
│   │   └── MainTabNavigator.tsx   # Main tabs
│   ├── services/          # API and business logic
│   │   ├── api/           # API client and services
│   │   ├── storage/       # Local storage
│   │   ├── sync/          # Offline sync
│   │   └── notifications/ # Push notifications
│   ├── store/             # Zustand stores
│   │   └── authStore.ts   # Auth state management
│   ├── types/             # TypeScript type definitions
│   │   └── models/        # Data models (copied from desktop)
│   ├── theme/             # Theme configuration
│   │   └── colors.ts      # Colors, spacing, fonts
│   └── utils/             # Utility functions
├── assets/                # Images, fonts, icons
├── App.tsx                # Root component
├── app.json               # Expo configuration
├── package.json           # Dependencies
└── tsconfig.json          # TypeScript config
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm 9+
- Expo CLI: `npm install -g expo-cli`
- iOS Simulator (Xcode) for iOS development
- Android Emulator (Android Studio) for Android development
- **Backend running** at `http://localhost:8001`

### Installation

```bash
# Navigate to mobile directory
cd mobile

# Install dependencies (already done)
npm install

# Start development server
npm start
```

### Running on Devices

```bash
# iOS Simulator (macOS only)
npm run ios

# Android Emulator
npm run android

# Web (for quick testing)
npm run web

# Expo Go app (scan QR code)
npm start
# Then scan QR code with Expo Go app
```

## 📱 Features Implemented (Phase 1)

### ✅ Authentication
- Login screen with email/password
- Register screen with validation
- JWT token storage in SecureStore
- Auto-login on app launch
- Logout functionality

### ✅ API Integration
- Axios HTTP client with interceptors
- JWT token refresh flow (401 handling)
- Secure token storage (Expo SecureStore)
- Error handling and user-friendly messages

### ✅ State Management
- Zustand store for auth state
- User profile management
- Loading and error states

### ✅ Navigation
- React Navigation with Stack and Bottom Tabs
- Auth flow (Login ↔ Register)
- Main tabs (Calendar, Stats, AI, Profile)
- Auto-navigation based on auth status

### ✅ UI Components
- React Native Paper integration
- Custom theme with brand colors
- Form validation with error messages
- Loading indicators
- Responsive layouts

## 🔜 Next Steps (Phase 2-6)

### Phase 2: Calendar & Day View (Week 3-4)
- [ ] Calendar month view with react-native-calendars
- [ ] Day screen with 7 tabs (Overview, Meals, Exercise, Water, Sleep, Mood, Notes)
- [ ] CRUD operations for meals and exercises
- [ ] Weight tracking input

### Phase 3: Statistics & Charts (Week 5)
- [ ] Weight trend chart
- [ ] Calories chart
- [ ] Water intake chart
- [ ] Sleep and exercise charts
- [ ] Date range selector

### Phase 4: AI Agents (Week 6)
- [ ] Chatbot screen with message bubbles
- [ ] Vision Agent (camera/photo picker)
- [ ] Nutrition and Workout Coach dialogs
- [ ] Daily Summary integration

### Phase 5: Offline Support (Week 7)
- [ ] WatermelonDB setup
- [ ] Local data caching
- [ ] Sync engine
- [ ] Offline mode handling

### Phase 6: Notifications & Settings (Week 8)
- [ ] Push notifications setup
- [ ] Daily reminders
- [ ] Profile settings
- [ ] Language switcher (i18n)
- [ ] HealthKit/Google Fit integration

## 🔐 Environment Configuration

### Backend URL

Currently set to `http://localhost:8001/api/v1` in `src/services/api/apiClient.ts`.

**For device testing**, update to your computer's local IP:

```typescript
// src/services/api/apiClient.ts
const API_BASE_URL = 'http://192.168.1.XXX:8001/api/v1';  // Replace with your IP
```

### Finding Your Local IP

**macOS/Linux:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Windows:**
```bash
ipconfig
```

## 🧪 Testing

### Manual Testing

1. **Start backend server:**
   ```bash
   cd ../backend
   source venv/bin/activate
   python main.py
   ```

2. **Start mobile app:**
   ```bash
   cd mobile
   npm start
   ```

3. **Test registration:**
   - Open app in simulator/device
   - Navigate to Register screen
   - Fill form and submit
   - Verify auto-login to Calendar screen

4. **Test login:**
   - Logout from Calendar screen
   - Login with registered credentials
   - Verify navigation to Calendar screen

5. **Test token refresh:**
   - Stay logged in for > 30 minutes
   - Make API call (should auto-refresh token)

## 📦 Build Commands

### Development Build

```bash
# iOS
eas build --profile development --platform ios

# Android
eas build --profile development --platform android
```

### Production Build

```bash
# iOS (for App Store)
eas build --profile production --platform ios

# Android (for Play Store)
eas build --profile production --platform android
```

## 🔗 API Endpoints Used

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update user profile

## 📖 Documentation

- [React Native Docs](https://reactnative.dev/)
- [Expo Docs](https://docs.expo.dev/)
- [React Navigation](https://reactnavigation.org/)
- [React Native Paper](https://callstack.github.io/react-native-paper/)
- [Zustand Docs](https://zustand-demo.pmnd.rs/)
- [Mobile Apps Development Plan](../docs/MOBILE_APPS_PLAN.md)

## 🐛 Troubleshooting

### "Network Error" when testing on device

**Problem:** App can't connect to localhost backend.

**Solution:** Update `API_BASE_URL` to your computer's local IP address.

### "Expo Go app not connecting"

**Problem:** QR code scan doesn't work.

**Solution:**
1. Ensure phone and computer are on same Wi-Fi network
2. Disable VPN if active
3. Try tunnel mode: `expo start --tunnel`

### "SecureStore not available"

**Problem:** SecureStore only works on real devices/simulators, not web.

**Solution:** Use device/simulator for testing auth features.

## 👥 Development Team

Phase 1 (Auth & Infrastructure) completed. Ready for Phase 2 implementation.

## 📝 License

MIT License - Same as parent project

---

**Status**: Phase 1 Complete ✅
**Next Phase**: Calendar & Day View
**Estimated Time**: 2 weeks
