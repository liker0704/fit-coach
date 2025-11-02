# FitCoach iOS

**Personal Health Tracker - Native iOS Client (Swift + SwiftUI)**

[![Swift](https://img.shields.io/badge/Swift-5.9+-orange.svg)](https://swift.org)
[![iOS](https://img.shields.io/badge/iOS-15.0+-blue.svg)](https://developer.apple.com/ios/)
[![SwiftUI](https://img.shields.io/badge/SwiftUI-3.0+-blue.svg)](https://developer.apple.com/xcode/swiftui/)
[![Status](https://img.shields.io/badge/Status-Planned-lightgrey.svg)](#)

---

## 📋 Overview

FitCoach iOS is a native mobile application for iPhone and iPad, providing a seamless health tracking experience with AI-powered coaching. Built with Swift and SwiftUI, it offers offline-first functionality with CoreData caching and full sync with the FitCoach backend API.

**Status**: 📋 Planned (Specifications complete, implementation not started)

**Backend API**: Requires FitCoach backend running at configured URL

---

## ✨ Planned Features

### Core Functionality

#### ✅ Phase 1: Authentication & Profile (Week 1-2)
- [ ] Login screen with email/password
- [ ] Register screen with validation
- [ ] JWT token management (Keychain storage)
- [ ] Auto-refresh token on 401 responses
- [ ] User profile view
- [ ] Profile editing (height, weight, DOB, goals)
- [ ] Logout functionality

#### ✅ Phase 2: Calendar & Day View (Week 3-5)
- [ ] Monthly calendar grid view
- [ ] Day cards with preview (meals count, exercises count, water %)
- [ ] Color-coded effort scores
- [ ] Swipe to navigate months
- [ ] Tap day to open detail view
- [ ] Date picker for quick navigation
- [ ] Today button

#### ✅ Phase 3: Health Tracking - Day Detail (Week 6-9)
**7 Main Sections:**

1. **Meals Section** (Week 6)
   - [ ] List of meals grouped by category
   - [ ] Add meal form with nutrition input
   - [ ] Edit/delete meals with swipe actions
   - [ ] Total calories and macros for day
   - [ ] Meal category picker (Breakfast, Lunch, Dinner, Snack)

2. **Exercises Section** (Week 7)
   - [ ] List of exercises with type icons
   - [ ] Add exercise form (type, duration, distance, intensity)
   - [ ] Edit/delete exercises
   - [ ] Total exercise minutes for day
   - [ ] Heart rate input (optional)

3. **Water Intake Section** (Week 7)
   - [ ] Visual water glasses UI
   - [ ] Progress ring showing goal (2.5-3L)
   - [ ] Quick add buttons (250ml, 500ml, 1L)
   - [ ] Custom amount input
   - [ ] Total intake display

4. **Sleep Section** (Week 8)
   - [ ] Sleep start/end time pickers
   - [ ] Auto-calculated duration
   - [ ] Quality rating (1-5 stars)
   - [ ] Sleep notes (optional)
   - [ ] Hours and minutes display

5. **Mood Section** (Week 8)
   - [ ] Mood rating slider (1-5 with emojis)
   - [ ] Multi-select tags (Stress, Focus, Energy, etc.)
   - [ ] Mood notes textarea
   - [ ] Visual mood history

6. **Notes Section** (Week 9)
   - [ ] Rich text editor for daily notes
   - [ ] Markdown support (bold, italic, lists)
   - [ ] Auto-save on blur
   - [ ] Character count

7. **AI Summary Section** (Week 9)
   - [ ] "Generate Summary" button
   - [ ] Loading state with animation
   - [ ] Display AI-generated summary
   - [ ] Effort score visualization (0-10)
   - [ ] Regenerate functionality

#### ✅ Phase 4: Statistics & Charts (Week 10-12)
- [ ] Statistics tab with 7 charts
- [ ] Date range selector (7/30/90 days)
- [ ] Interactive charts using Swift Charts
- [ ] Chart types:
  - Weight line chart
  - Activity bar chart
  - Nutrition multi-line chart
  - Water bar chart
  - Sleep duration chart
  - Mood trend chart
  - Effort score chart
- [ ] Export data to CSV (future)

#### ✅ Phase 5: Settings & Preferences (Week 13)
- [ ] Settings screen
- [ ] Profile editing
- [ ] Goals configuration (water, calories, sleep)
- [ ] App theme (Light/Dark/System)
- [ ] Notification preferences
- [ ] Language selection (EN/RU/CZ)
- [ ] About & version info
- [ ] Logout button

#### ✅ Phase 6: Offline Mode & Sync (Week 14-15)
- [ ] CoreData local storage
- [ ] Offline create/edit/delete operations
- [ ] Sync queue for pending changes
- [ ] Background sync when online
- [ ] Conflict resolution (server wins)
- [ ] Sync status indicator
- [ ] Manual sync trigger

#### ✅ Phase 7: Polish & Optimization (Week 16)
- [ ] App icon & launch screen
- [ ] Haptic feedback
- [ ] Animations & transitions
- [ ] Performance optimization
- [ ] Memory management
- [ ] Accessibility (VoiceOver, Dynamic Type)
- [ ] Localization strings

---

## 🏗️ Technical Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | **Swift 5.9+** | Type-safe, performant native development |
| UI Framework | **SwiftUI 3.0+** | Declarative UI, state management |
| Networking | **URLSession + Alamofire** | REST API client, JWT handling |
| Local Storage | **CoreData** | Offline persistence, caching |
| Charts | **Swift Charts** | Native data visualization |
| Authentication | **Keychain** | Secure token storage |
| Async | **async/await** | Modern concurrency |

### Minimum Requirements

- **iOS**: 15.0+
- **Xcode**: 14.0+
- **Swift**: 5.9+
- **Devices**: iPhone, iPad (universal)

---

## 📁 Project Structure (Planned)

```
FitCoach-iOS/
├── FitCoach.xcodeproj
├── FitCoach/
│   ├── App/
│   │   ├── FitCoachApp.swift          # App entry point
│   │   ├── AppDelegate.swift          # App lifecycle
│   │   └── Info.plist                 # App configuration
│   │
│   ├── Views/
│   │   ├── Auth/
│   │   │   ├── LoginView.swift
│   │   │   └── RegisterView.swift
│   │   ├── Calendar/
│   │   │   ├── CalendarView.swift     # Monthly grid
│   │   │   ├── DayCardView.swift      # Day preview card
│   │   │   └── DayDetailView.swift    # Day with 7 sections
│   │   ├── Health/
│   │   │   ├── MealsView.swift
│   │   │   ├── ExercisesView.swift
│   │   │   ├── WaterView.swift
│   │   │   ├── SleepView.swift
│   │   │   ├── MoodView.swift
│   │   │   ├── NotesView.swift
│   │   │   └── AISummaryView.swift
│   │   ├── Stats/
│   │   │   ├── StatsView.swift
│   │   │   ├── WeightChartView.swift
│   │   │   ├── ActivityChartView.swift
│   │   │   ├── NutritionChartView.swift
│   │   │   ├── WaterChartView.swift
│   │   │   ├── SleepChartView.swift
│   │   │   ├── MoodChartView.swift
│   │   │   └── EffortChartView.swift
│   │   ├── Profile/
│   │   │   ├── ProfileView.swift
│   │   │   └── EditProfileView.swift
│   │   ├── Settings/
│   │   │   ├── SettingsView.swift
│   │   │   ├── GoalsView.swift
│   │   │   └── AppearanceView.swift
│   │   └── Components/
│   │       ├── LoadingView.swift
│   │       ├── ErrorView.swift
│   │       ├── EmptyStateView.swift
│   │       └── CustomButton.swift
│   │
│   ├── ViewModels/
│   │   ├── AuthViewModel.swift
│   │   ├── CalendarViewModel.swift
│   │   ├── DayViewModel.swift
│   │   ├── MealViewModel.swift
│   │   ├── ExerciseViewModel.swift
│   │   ├── WaterViewModel.swift
│   │   ├── SleepViewModel.swift
│   │   ├── MoodViewModel.swift
│   │   ├── StatsViewModel.swift
│   │   └── ProfileViewModel.swift
│   │
│   ├── Models/
│   │   ├── User.swift
│   │   ├── Day.swift
│   │   ├── Meal.swift
│   │   ├── Exercise.swift
│   │   ├── WaterIntake.swift
│   │   ├── Sleep.swift
│   │   ├── Mood.swift
│   │   └── Note.swift
│   │
│   ├── Services/
│   │   ├── API/
│   │   │   ├── APIClient.swift        # Base HTTP client
│   │   │   ├── AuthService.swift
│   │   │   ├── DayService.swift
│   │   │   ├── MealService.swift
│   │   │   ├── ExerciseService.swift
│   │   │   ├── WaterService.swift
│   │   │   ├── SleepService.swift
│   │   │   ├── MoodService.swift
│   │   │   ├── NoteService.swift
│   │   │   └── AIService.swift
│   │   ├── Storage/
│   │   │   ├── CoreDataManager.swift  # CoreData stack
│   │   │   ├── KeychainManager.swift  # Secure storage
│   │   │   └── UserDefaultsManager.swift
│   │   └── Sync/
│   │       ├── SyncManager.swift      # Offline sync logic
│   │       └── SyncQueue.swift        # Pending operations
│   │
│   ├── CoreData/
│   │   ├── FitCoach.xcdatamodeld      # CoreData schema
│   │   └── NSManagedObject+Extensions.swift
│   │
│   ├── Utilities/
│   │   ├── Extensions/
│   │   │   ├── Date+Extensions.swift
│   │   │   ├── Color+Extensions.swift
│   │   │   └── View+Extensions.swift
│   │   ├── Constants.swift
│   │   ├── Logger.swift
│   │   └── Validators.swift
│   │
│   └── Resources/
│       ├── Assets.xcassets             # Images, colors, icons
│       ├── Localizable.strings         # Translations (EN/RU/CZ)
│       └── LaunchScreen.storyboard
│
├── FitCoachTests/
│   ├── ViewModelTests/
│   ├── ServiceTests/
│   └── ModelTests/
│
└── FitCoachUITests/
    ├── AuthFlowTests.swift
    ├── DayTrackingTests.swift
    └── SyncTests.swift
```

---

## 🚀 Getting Started (Future)

### Prerequisites
- macOS 13+ (Ventura or later)
- Xcode 14+
- iOS Simulator or physical iPhone/iPad
- FitCoach backend running at accessible URL

### Initial Setup (When Implementation Starts)

1. **Clone repository**
   ```bash
   cd /path/to/fit-coach
   ```

2. **Open in Xcode**
   ```bash
   cd ios
   open FitCoach.xcodeproj
   ```

3. **Configure Backend URL**
   ```swift
   // FitCoach/Utilities/Constants.swift
   struct APIConstants {
       static let baseURL = "http://localhost:8001/api/v1"
       // or
       static let baseURL = "https://api.fitcoach.com/api/v1"
   }
   ```

4. **Install Dependencies** (if using CocoaPods/SPM)
   ```bash
   # If using CocoaPods
   pod install
   open FitCoach.xcworkspace

   # If using Swift Package Manager
   # Dependencies managed in Xcode (File > Add Packages)
   ```

5. **Run on Simulator**
   - Select target device (e.g., iPhone 15 Pro)
   - Press ⌘R or click Run button
   - App will launch in simulator

6. **Run on Physical Device**
   - Connect iPhone/iPad via USB
   - Select device in Xcode
   - Configure signing (Team, Bundle ID)
   - Press ⌘R to build and run

---

## 🎨 Design System

### Colors (Planned)

```swift
extension Color {
    // Primary Colors
    static let primaryBlue = Color("PrimaryBlue")
    static let secondaryGreen = Color("SecondaryGreen")

    // Background
    static let backgroundLight = Color("BackgroundLight")
    static let backgroundDark = Color("BackgroundDark")

    // Effort Score Colors
    static let effortLow = Color.red
    static let effortMedium = Color.orange
    static let effortHigh = Color.green

    // Chart Colors
    static let chartWeight = Color.purple
    static let chartActivity = Color.blue
    static let chartNutrition = Color.green
}
```

### Typography

```swift
extension Font {
    static let heading1 = Font.system(size: 28, weight: .bold)
    static let heading2 = Font.system(size: 22, weight: .semibold)
    static let heading3 = Font.system(size: 18, weight: .medium)
    static let body = Font.system(size: 16, weight: .regular)
    static let caption = Font.system(size: 14, weight: .regular)
}
```

### Spacing

```swift
struct Spacing {
    static let xs: CGFloat = 4
    static let sm: CGFloat = 8
    static let md: CGFloat = 16
    static let lg: CGFloat = 24
    static let xl: CGFloat = 32
}
```

---

## 🔐 Authentication Flow

### JWT Token Management

```swift
// Services/Storage/KeychainManager.swift
class KeychainManager {
    func saveAccessToken(_ token: String) { }
    func saveRefreshToken(_ token: String) { }
    func getAccessToken() -> String? { }
    func getRefreshToken() -> String? { }
    func clearTokens() { }
}

// Services/API/APIClient.swift
class APIClient {
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        var request = URLRequest(url: endpoint.url)

        // Add Authorization header
        if let token = KeychainManager.shared.getAccessToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let (data, response) = try await URLSession.shared.data(for: request)

        // Handle 401 - refresh token
        if (response as? HTTPURLResponse)?.statusCode == 401 {
            try await refreshToken()
            return try await request(endpoint) // Retry
        }

        return try JSONDecoder().decode(T.self, from: data)
    }

    func refreshToken() async throws {
        // Call /auth/refresh with refresh token
        // Save new access token
    }
}
```

---

## 💾 Offline Storage with CoreData

### CoreData Entities

```swift
// CoreData/FitCoach.xcdatamodeld
@Entity Day {
    @Attribute var id: Int64
    @Attribute var userId: Int64
    @Attribute var date: Date
    @Attribute var tags: [String]
    @Attribute var wellnessScore: Int16
    @Attribute var effortScore: Int16
    @Attribute var synced: Bool
    @Attribute var deleted: Bool
    @Relationship var meals: Set<Meal>
    @Relationship var exercises: Set<Exercise>
}

@Entity Meal {
    @Attribute var id: Int64
    @Attribute var name: String
    @Attribute var category: String
    @Attribute var calories: Int32
    @Attribute var synced: Bool
    @Relationship var day: Day
}
```

### Sync Logic

```swift
// Services/Sync/SyncManager.swift
class SyncManager {
    func syncPendingChanges() async throws {
        // 1. Fetch unsynced records from CoreData
        let unsyncedDays = fetchUnsyncedDays()

        // 2. Upload to server
        for day in unsyncedDays {
            try await uploadDay(day)
            day.synced = true
        }

        // 3. Download new data from server
        let serverDays = try await fetchDaysFromServer()

        // 4. Update local database
        for serverDay in serverDays {
            updateOrInsertDay(serverDay)
        }
    }

    func scheduleBackgroundSync() {
        // Use BackgroundTasks framework
        // Sync every 15 minutes when app is backgrounded
    }
}
```

---

## 📊 Charts with Swift Charts

### Example: Weight Chart

```swift
import Charts

struct WeightChartView: View {
    let data: [WeightEntry]

    var body: some View {
        Chart(data) { entry in
            LineMark(
                x: .value("Date", entry.date),
                y: .value("Weight", entry.weight)
            )
            .foregroundStyle(.purple)
            .interpolationMethod(.catmullRom)

            // Goal line
            RuleMark(y: .value("Goal", 75))
                .foregroundStyle(.gray)
                .lineStyle(StrokeStyle(lineWidth: 1, dash: [5, 5]))
        }
        .chartYScale(domain: 60...90)
        .chartYAxis {
            AxisMarks(position: .leading)
        }
    }
}
```

---

## 🧪 Testing Strategy

### Unit Tests

```swift
// FitCoachTests/ViewModelTests/DayViewModelTests.swift
import XCTest
@testable import FitCoach

final class DayViewModelTests: XCTestCase {
    var viewModel: DayViewModel!
    var mockService: MockDayService!

    override func setUp() {
        super.setUp()
        mockService = MockDayService()
        viewModel = DayViewModel(service: mockService)
    }

    func testFetchDaySuccess() async throws {
        // Given
        let expectedDay = Day(id: 1, date: Date())
        mockService.mockDay = expectedDay

        // When
        await viewModel.fetchDay(date: Date())

        // Then
        XCTAssertEqual(viewModel.currentDay?.id, 1)
        XCTAssertFalse(viewModel.isLoading)
    }
}
```

### UI Tests

```swift
// FitCoachUITests/AuthFlowTests.swift
import XCTest

final class AuthFlowTests: XCTestCase {
    let app = XCUIApplication()

    func testLoginFlow() {
        app.launch()

        // Enter credentials
        let emailField = app.textFields["Email"]
        emailField.tap()
        emailField.typeText("test@example.com")

        let passwordField = app.secureTextFields["Password"]
        passwordField.tap()
        passwordField.typeText("password123")

        // Tap login button
        app.buttons["Login"].tap()

        // Verify navigation to calendar
        XCTAssertTrue(app.navigationBars["Calendar"].exists)
    }
}
```

---

## 📦 Dependencies (Planned)

### Swift Package Manager

```swift
// Package.swift dependencies
dependencies: [
    .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0"),
    .package(url: "https://github.com/SwiftyJSON/SwiftyJSON.git", from: "5.0.0"),
]
```

**Note**: Minimize external dependencies; use native frameworks when possible.

---

## 🚧 Implementation Roadmap

### Estimated Timeline: 16 weeks (4 months)

| Week | Phase | Tasks | Status |
|------|-------|-------|--------|
| 1-2 | Auth & Profile | Login, Register, JWT, Keychain | ⏳ |
| 3-5 | Calendar | Grid view, day cards, navigation | ⏳ |
| 6 | Meals | Meal CRUD, nutrition input | ⏳ |
| 7 | Exercises & Water | Exercise CRUD, water tracker | ⏳ |
| 8 | Sleep & Mood | Sleep tracker, mood rating | ⏳ |
| 9 | Notes & AI | Notes editor, AI summary | ⏳ |
| 10-12 | Statistics | 7 charts, date range selector | ⏳ |
| 13 | Settings | Profile edit, goals, preferences | ⏳ |
| 14-15 | Offline Sync | CoreData, sync manager | ⏳ |
| 16 | Polish | Icon, animations, accessibility | ⏳ |

**Total Effort**: ~640 hours (16 weeks × 40 hours/week)

---

## 🎯 Success Criteria

### Performance Metrics
- [ ] App startup time < 1 second
- [ ] API response handling < 200ms
- [ ] Smooth 60 FPS scrolling in calendar and lists
- [ ] Offline mode fully functional

### Quality Metrics
- [ ] Zero crashes in production
- [ ] Test coverage > 70%
- [ ] App size < 50MB
- [ ] Battery usage optimized

### User Experience
- [ ] Intuitive navigation
- [ ] Responsive UI (no lag)
- [ ] Offline-first experience
- [ ] Accessibility compliant (VoiceOver, Dynamic Type)

---

## 📚 Resources

- [Swift Documentation](https://swift.org/documentation/)
- [SwiftUI Tutorials](https://developer.apple.com/tutorials/swiftui)
- [Swift Charts](https://developer.apple.com/documentation/charts)
- [CoreData Guide](https://developer.apple.com/documentation/coredata)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Keychain Services](https://developer.apple.com/documentation/security/keychain_services)

---

## 🔗 Related Documentation

- [Root README](../README.md) - Project overview
- [Backend API](../backend/README.md) - REST API documentation
- [API Specification](../docs/api-specification.md) - Endpoint details
- [Implementation Plan](../docs/implementation-plan.md) - Full project roadmap

---

## ⚠️ Current Status

**This iOS client is in the planning phase.** Implementation will begin after:
1. ✅ Backend MVP is complete (Done)
2. 🔨 Desktop client reaches stable release (In Progress)
3. 📋 Mobile-specific features are prioritized

**Expected Start Date**: Q2 2025

---

**Last Updated**: 2025-11-02
**Status**: Specifications Complete - Awaiting Implementation

For questions about iOS development, please open an issue on GitHub.
