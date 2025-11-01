# API Specification - OpenAPI 3.0

## Полная спецификация REST API FitCoach

### Базовая информация
```yaml
openapi: 3.0.3
info:
  title: FitCoach API
  description: Personal health and habits tracker with AI coach
  version: 1.0.0
  contact:
    name: FitCoach Support
    email: support@fitcoach.app

servers:
  - url: http://localhost:8000/api/v1
    description: Development server
  - url: https://api.fitcoach.app/v1
    description: Production server

security:
  - bearerAuth: []
```

## Authentication Endpoints

### POST /auth/register
```yaml
summary: Register new user
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        required:
          - email
          - password
        properties:
          email:
            type: string
            format: email
          password:
            type: string
            minLength: 8
          full_name:
            type: string
          age:
            type: integer
            minimum: 1
            maximum: 150
          height:
            type: number
            description: Height in cm
          weight:
            type: number
            description: Weight in kg
      example:
        email: user@example.com
        password: securePassword123
        full_name: John Doe
        age: 30
        height: 180
        weight: 75

responses:
  200:
    description: Successfully registered
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
  400:
    description: User already exists
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
```

### POST /auth/login
```yaml
summary: Login user
requestBody:
  required: true
  content:
    application/x-www-form-urlencoded:
      schema:
        type: object
        required:
          - username
          - password
        properties:
          username:
            type: string
            description: Email address
          password:
            type: string
      example:
        username: user@example.com
        password: securePassword123

responses:
  200:
    description: Successfully logged in
    content:
      application/json:
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            token_type:
              type: string
              default: bearer
        example:
          access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
          refresh_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
          token_type: bearer
  401:
    description: Invalid credentials
```

### POST /auth/refresh
```yaml
summary: Refresh access token
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        required:
          - refresh_token
        properties:
          refresh_token:
            type: string

responses:
  200:
    description: Token refreshed
    content:
      application/json:
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            token_type:
              type: string
```

## User Endpoints

### GET /users/me
```yaml
summary: Get current user
security:
  - bearerAuth: []

responses:
  200:
    description: User profile
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
        example:
          id: 1
          email: user@example.com
          username: johndoe
          full_name: John Doe
          age: 30
          height: 180
          weight: 75
          water_goal: 2.5
          calorie_goal: 2000
          sleep_goal: 8
          created_at: "2024-01-01T00:00:00Z"
```

### PUT /users/me
```yaml
summary: Update current user
security:
  - bearerAuth: []
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        properties:
          full_name:
            type: string
          age:
            type: integer
          height:
            type: number
          weight:
            type: number
          target_weight:
            type: number
          water_goal:
            type: number
          calorie_goal:
            type: integer
          sleep_goal:
            type: number

responses:
  200:
    description: Updated user
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
```

## Day Endpoints

### GET /days
```yaml
summary: Get list of days
security:
  - bearerAuth: []
parameters:
  - in: query
    name: start_date
    schema:
      type: string
      format: date
    description: Start date filter
  - in: query
    name: end_date
    schema:
      type: string
      format: date
    description: End date filter
  - in: query
    name: skip
    schema:
      type: integer
      default: 0
    description: Number of items to skip
  - in: query
    name: limit
    schema:
      type: integer
      default: 100
      maximum: 100
    description: Number of items to return
  - in: query
    name: include_details
    schema:
      type: boolean
      default: false
    description: Include all related data

responses:
  200:
    description: List of days
    content:
      application/json:
        schema:
          type: object
          properties:
            days:
              type: array
              items:
                $ref: '#/components/schemas/Day'
            total:
              type: integer
            page:
              type: integer
            per_page:
              type: integer
        example:
          days:
            - date: "2024-01-01"
              tag: "New Year"
              feeling: 5
              effort_score: 8.5
              total_calories: 2100
              total_water: 2.8
              total_exercise_minutes: 45
          total: 50
          page: 1
          per_page: 100
```

### GET /days/{date}
```yaml
summary: Get specific day
security:
  - bearerAuth: []
parameters:
  - in: path
    name: date
    required: true
    schema:
      type: string
      format: date
    example: "2024-01-01"
  - in: query
    name: include_meals
    schema:
      type: boolean
      default: true
  - in: query
    name: include_exercises
    schema:
      type: boolean
      default: true
  - in: query
    name: include_water
    schema:
      type: boolean
      default: true
  - in: query
    name: include_sleep
    schema:
      type: boolean
      default: true
  - in: query
    name: include_mood
    schema:
      type: boolean
      default: true
  - in: query
    name: include_notes
    schema:
      type: boolean
      default: true
  - in: query
    name: include_summary
    schema:
      type: boolean
      default: true

responses:
  200:
    description: Day details
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/DayFull'
  404:
    description: Day not found
```

### POST /days
```yaml
summary: Create new day
security:
  - bearerAuth: []
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        required:
          - date
        properties:
          date:
            type: string
            format: date
          tag:
            type: string
          feeling:
            type: integer
            minimum: 1
            maximum: 5

responses:
  201:
    description: Day created
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Day'
  400:
    description: Day already exists
```

## Meal Endpoints

### POST /days/{date}/meals
```yaml
summary: Add meal to day
security:
  - bearerAuth: []
parameters:
  - in: path
    name: date
    required: true
    schema:
      type: string
      format: date
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        required:
          - category
        properties:
          category:
            type: string
            enum: [breakfast, lunch, dinner, snack]
          time:
            type: string
            format: time
          calories:
            type: number
          protein:
            type: number
          carbs:
            type: number
          fat:
            type: number
          items:
            type: array
            items:
              type: object
              properties:
                name:
                  type: string
                amount:
                  type: number
                unit:
                  type: string
                calories:
                  type: number
          notes:
            type: string
      example:
        category: breakfast
        calories: 450
        protein: 20
        carbs: 60
        fat: 15
        items:
          - name: Oatmeal
            amount: 100
            unit: g
            calories: 300
          - name: Banana
            amount: 1
            unit: piece
            calories: 100
          - name: Almonds
            amount: 20
            unit: g
            calories: 50

responses:
  201:
    description: Meal added
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Meal'
```

## Exercise Endpoints

### POST /days/{date}/exercises
```yaml
summary: Add exercise to day
security:
  - bearerAuth: []
parameters:
  - in: path
    name: date
    required: true
    schema:
      type: string
      format: date
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        required:
          - type
        properties:
          type:
            type: string
            enum: [running, gym, yoga, cycling, swimming, walking, other]
          name:
            type: string
          start_time:
            type: string
            format: date-time
          duration:
            type: integer
            description: Duration in minutes
          distance:
            type: number
            description: Distance in km
          calories_burned:
            type: number
          heart_rate_avg:
            type: integer
          heart_rate_max:
            type: integer
          intensity:
            type: integer
            minimum: 1
            maximum: 5
          notes:
            type: string
      example:
        type: running
        name: Morning jog
        duration: 30
        distance: 5
        calories_burned: 350
        heart_rate_avg: 140
        intensity: 3

responses:
  201:
    description: Exercise added
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Exercise'
```

## Water Endpoints

### POST /days/{date}/water
```yaml
summary: Add water intake
security:
  - bearerAuth: []
parameters:
  - in: path
    name: date
    required: true
    schema:
      type: string
      format: date
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        required:
          - amount
        properties:
          amount:
            type: number
            description: Amount in liters
            minimum: 0.1
            maximum: 5.0
      example:
        amount: 0.5

responses:
  201:
    description: Water intake added
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/WaterIntake'
```

## LLM Summary Endpoints

### POST /days/{date}/summary
```yaml
summary: Generate AI summary for day
security:
  - bearerAuth: []
parameters:
  - in: path
    name: date
    required: true
    schema:
      type: string
      format: date
  - in: query
    name: regenerate
    schema:
      type: boolean
      default: false
    description: Regenerate even if summary exists

responses:
  200:
    description: Summary generated
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/LLMSummary'
        example:
          summary_text: "Great day overall! You maintained excellent nutrition balance with 2100 calories..."
          effort_score: 8.5
          score_reason: "Strong adherence to goals with good balance across all areas"
          tomorrow_advice: "Try to increase water intake by 0.5L and add 10 minutes to your morning exercise"
          model_used: "gpt-4-turbo"
          tokens_used: 850
  404:
    description: Day not found
  500:
    description: LLM generation failed
```

## Statistics Endpoints

### GET /statistics/week
```yaml
summary: Get weekly statistics
security:
  - bearerAuth: []
parameters:
  - in: query
    name: date
    schema:
      type: string
      format: date
    description: Any date in the target week (defaults to current week)

responses:
  200:
    description: Weekly statistics
    content:
      application/json:
        schema:
          type: object
          properties:
            start_date:
              type: string
              format: date
            end_date:
              type: string
              format: date
            days_logged:
              type: integer
            average_calories:
              type: number
            average_water:
              type: number
            total_exercise_minutes:
              type: integer
            average_sleep:
              type: number
            average_mood:
              type: number
            average_effort:
              type: number
            trends:
              type: object
              properties:
                calories:
                  type: string
                  enum: [up, down, stable]
                water:
                  type: string
                  enum: [up, down, stable]
                exercise:
                  type: string
                  enum: [up, down, stable]
```

## Components

### Schemas

#### User
```yaml
type: object
properties:
  id:
    type: integer
  email:
    type: string
    format: email
  username:
    type: string
  full_name:
    type: string
  age:
    type: integer
  height:
    type: number
  weight:
    type: number
  target_weight:
    type: number
  water_goal:
    type: number
  calorie_goal:
    type: integer
  sleep_goal:
    type: number
  language:
    type: string
  timezone:
    type: string
  is_active:
    type: boolean
  is_verified:
    type: boolean
  created_at:
    type: string
    format: date-time
  updated_at:
    type: string
    format: date-time
```

#### Day
```yaml
type: object
properties:
  id:
    type: integer
  date:
    type: string
    format: date
  tag:
    type: string
  feeling:
    type: integer
    minimum: 1
    maximum: 5
  effort_score:
    type: number
    minimum: 0
    maximum: 10
  summary:
    type: string
  llm_advice:
    type: string
  total_calories:
    type: number
  total_water:
    type: number
  total_exercise_minutes:
    type: integer
```

#### DayFull
```yaml
allOf:
  - $ref: '#/components/schemas/Day'
  - type: object
    properties:
      meals:
        type: array
        items:
          $ref: '#/components/schemas/Meal'
      exercises:
        type: array
        items:
          $ref: '#/components/schemas/Exercise'
      water_intakes:
        type: array
        items:
          $ref: '#/components/schemas/WaterIntake'
      sleep_records:
        type: array
        items:
          $ref: '#/components/schemas/Sleep'
      mood_records:
        type: array
        items:
          $ref: '#/components/schemas/Mood'
      notes:
        type: array
        items:
          $ref: '#/components/schemas/Note'
      llm_summary:
        $ref: '#/components/schemas/LLMSummary'
```

### Security Schemes
```yaml
bearerAuth:
  type: http
  scheme: bearer
  bearerFormat: JWT
```

### Error Responses
```yaml
Error:
  type: object
  properties:
    detail:
      type: string
    code:
      type: string
    field:
      type: string

ValidationError:
  type: object
  properties:
    detail:
      type: array
      items:
        type: object
        properties:
          loc:
            type: array
            items:
              type: string
          msg:
            type: string
          type:
            type: string
```

## Rate Limiting

Все endpoints имеют следующие ограничения:
- 100 запросов в минуту для аутентифицированных пользователей
- 20 запросов в минуту для неаутентифицированных
- LLM endpoints: 10 запросов в час

Headers в ответе:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Примеры использования

### cURL
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"

# Get current user
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"

# Create day
curl -X POST http://localhost:8000/api/v1/days \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"date": "2024-01-01", "tag": "New Year", "feeling": 5}'
```

### JavaScript/Axios
```javascript
// Setup
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Auth interceptor
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Login
const login = async (email, password) => {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)

  const response = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })

  localStorage.setItem('access_token', response.data.access_token)
  localStorage.setItem('refresh_token', response.data.refresh_token)
}

// Get day
const getDay = async (date) => {
  const response = await api.get(`/days/${date}`)
  return response.data
}

// Add meal
const addMeal = async (date, meal) => {
  const response = await api.post(`/days/${date}/meals`, meal)
  return response.data
}
```

### Python
```python
import requests
from datetime import date

class FitCoachAPI:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()

    def login(self, email, password):
        response = self.session.post(
            f"{self.base_url}/auth/login",
            data={"username": email, "password": password}
        )
        response.raise_for_status()

        data = response.json()
        self.session.headers["Authorization"] = f"Bearer {data['access_token']}"
        return data

    def get_day(self, day_date):
        response = self.session.get(f"{self.base_url}/days/{day_date}")
        response.raise_for_status()
        return response.json()

    def add_meal(self, day_date, meal):
        response = self.session.post(
            f"{self.base_url}/days/{day_date}/meals",
            json=meal
        )
        response.raise_for_status()
        return response.json()

# Usage
api = FitCoachAPI()
api.login("user@example.com", "password123")

day = api.get_day("2024-01-01")
meal = api.add_meal("2024-01-01", {
    "category": "breakfast",
    "calories": 450,
    "protein": 20,
    "carbs": 60,
    "fat": 15
})
```