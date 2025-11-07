# AI Agents API Documentation

Complete API reference for all AI agents in the FitCoach application.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Daily Summary Agent](#daily-summary-agent)
  - [Chatbot Agent](#chatbot-agent)
  - [Nutrition Coach Agent](#nutrition-coach-agent)
  - [Workout Coach Agent](#workout-coach-agent)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

---

## Overview

The AI Agents system provides personalized coaching and insights through specialized LLM-powered agents. Each agent has access to the user's health data and provides contextual advice.

**Base URL**: `http://your-domain.com/api/v1/agents`

**All endpoints require authentication** via JWT token in the Authorization header.

---

## Authentication

All agent endpoints require a valid JWT token:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

Get your token by logging in via `/api/v1/auth/login`.

---

## Endpoints

### Daily Summary Agent

Generates a comprehensive summary of your day's activities, nutrition, and progress.

**Endpoint**: `POST /agents/daily-summary`

**Request Body**:
```json
{
  "date": "2025-11-07"  // Optional, defaults to today (ISO format)
}
```

**Response** (200 OK):
```json
{
  "summary": "You had a great day today! You completed 2 workouts...",
  "date": "2025-11-07",
  "highlights": [
    "Completed 2 workouts totaling 90 minutes",
    "Hit your protein goal of 150g",
    "Maintained a 500 calorie deficit"
  ],
  "recommendations": [
    "Try to get 8 hours of sleep tonight",
    "Increase water intake tomorrow - you only drank 1.5L today",
    "Consider adding a rest day this week"
  ],
  "generated_at": "2025-11-07T14:30:00Z"
}
```

**Features**:
- Analyzes all day data: meals, exercises, sleep, mood, water
- Compares progress against user goals
- Provides actionable recommendations
- Highlights achievements and patterns

**Example cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/agents/daily-summary" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-11-07"}'
```

---

### Chatbot Agent

General fitness assistant for conversational Q&A about health, fitness, and wellness.

**Endpoint**: `POST /agents/chat`

**Request Body**:
```json
{
  "message": "What's the best way to build muscle?",
  "conversation_history": [  // Optional, for multi-turn conversations
    {
      "role": "user",
      "content": "I want to get stronger"
    },
    {
      "role": "assistant",
      "content": "That's great! Building strength requires..."
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "response": "Building muscle requires three key components: progressive resistance training, adequate protein intake (1.6-2.2g per kg bodyweight), and sufficient recovery. Focus on compound movements like squats, deadlifts, and bench press...",
  "generated_at": "2025-11-07T14:30:00Z"
}
```

**Features**:
- Conversational AI with context awareness
- Supports multi-turn conversations via history
- Friendly, motivating personality
- No access to user data (use coaches for personalized advice)

**Example cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/agents/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How much protein should I eat?",
    "conversation_history": []
  }'
```

---

### Nutrition Coach Agent

Personalized nutrition coaching based on your goals and current progress.

**Endpoint**: `POST /agents/nutrition-coach`

**Request Body**:
```json
{
  "message": "How can I optimize my nutrition for muscle gain?",
  "date": "2025-11-07"  // Optional, for context on specific day
}
```

**Response** (200 OK):
```json
{
  "response": "Based on your current stats (75kg, aiming for 80kg) and recent nutrition data, here's my advice:\n\n1. **Increase Protein**: You're averaging 120g/day, but for muscle gain aim for 150-165g (2-2.2g/kg).\n\n2. **Carb Timing**: Your workout days show better energy when you eat carbs 1-2 hours before training. Continue this pattern.\n\n3. **Caloric Surplus**: You're in a slight deficit. Add 200-300 calories per day, primarily from complex carbs and healthy fats.\n\n4. **Meal Frequency**: Your 3-meal pattern is fine, but consider adding a post-workout shake for better recovery.",
  "generated_at": "2025-11-07T14:30:00Z"
}
```

**Features**:
- Context-aware: accesses your recent nutrition data
- Goal-oriented: aligns advice with your fitness goals
- Evidence-based recommendations
- Specific, actionable suggestions

**Example cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/agents/nutrition-coach" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Am I eating enough protein?",
    "date": "2025-11-07"
  }'
```

---

### Workout Coach Agent

Personalized workout coaching and training advice based on your activity.

**Endpoint**: `POST /agents/workout-coach`

**Request Body**:
```json
{
  "message": "What exercises should I focus on for strength?",
  "date": "2025-11-07"  // Optional, for context on specific day
}
```

**Response** (200 OK):
```json
{
  "response": "Great question! Based on your training history and goals, here's what I recommend:\n\n**Core Strength Movements:**\n1. **Squat** - 3-4 sets of 6-8 reps (you've been doing 10-12, time to increase weight and lower reps)\n2. **Deadlift** - 3 sets of 5 reps (add this back - you haven't deadlifted in 2 weeks)\n3. **Bench Press** - 4 sets of 6-8 reps\n4. **Overhead Press** - 3 sets of 8-10 reps\n\n**Progressive Overload:**\nYour squat has plateaued at 100kg for 3 weeks. Try adding 2.5kg and dropping to 6 reps. Or add a pause at the bottom to build strength.\n\n**Recovery:**\nYou've trained 5 days straight. Consider a rest day or active recovery to prevent overtraining.",
  "generated_at": "2025-11-07T14:30:00Z"
}
```

**Features**:
- Analyzes your workout history and patterns
- Identifies plateaus and suggests solutions
- Provides progressive overload strategies
- Safety-focused (warns about overtraining, form issues)
- Goal-aligned programming

**Example cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/agents/workout-coach" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My squat has plateaued, what should I do?",
    "date": "2025-11-07"
  }'
```

---

## Error Handling

All endpoints use standard HTTP status codes:

### Common Error Responses

**401 Unauthorized** - Missing or invalid JWT token:
```json
{
  "detail": "Not authenticated"
}
```

**422 Unprocessable Entity** - Invalid request body:
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error** - Agent execution failed:
```json
{
  "detail": "Agent execution failed: LLM API error"
}
```

### Error Handling Best Practices

1. **Always check status codes** before parsing response
2. **Handle 401** by refreshing token or re-authenticating
3. **Handle 422** by validating input before sending
4. **Handle 500** with retry logic (exponential backoff)
5. **Show user-friendly messages** instead of raw error details

---

## Rate Limiting

**Current Limits**: No rate limits enforced (development mode)

**Production Recommendations**:
- Daily Summary: 50 requests/day per user
- Chatbot: 100 requests/day per user
- Nutrition Coach: 50 requests/day per user
- Workout Coach: 50 requests/day per user

Rate limits will be enforced based on JWT token user_id.

---

## Examples

### Complete Flow: Daily Summary + Follow-up Coaching

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_jwt_token_here"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. Get daily summary
summary_response = requests.post(
    f"{BASE_URL}/agents/daily-summary",
    json={"date": "2025-11-07"},
    headers=HEADERS
)
summary = summary_response.json()
print("Summary:", summary["summary"])
print("Recommendations:", summary["recommendations"])

# 2. Ask nutrition coach about a specific recommendation
if "protein" in summary["summary"].lower():
    nutrition_response = requests.post(
        f"{BASE_URL}/agents/nutrition-coach",
        json={
            "message": "Can you give me specific meal ideas to hit my protein goal?",
            "date": "2025-11-07"
        },
        headers=HEADERS
    )
    print("Nutrition Advice:", nutrition_response.json()["response"])

# 3. Ask workout coach about training
workout_response = requests.post(
    f"{BASE_URL}/agents/workout-coach",
    json={
        "message": "What exercises should I do tomorrow?",
        "date": "2025-11-07"
    },
    headers=HEADERS
)
print("Workout Advice:", workout_response.json()["response"])
```

### Multi-turn Chatbot Conversation

```python
conversation_history = []

# Turn 1
response1 = requests.post(
    f"{BASE_URL}/agents/chat",
    json={
        "message": "I want to lose weight",
        "conversation_history": conversation_history
    },
    headers=HEADERS
).json()

conversation_history.append({"role": "user", "content": "I want to lose weight"})
conversation_history.append({"role": "assistant", "content": response1["response"]})

# Turn 2
response2 = requests.post(
    f"{BASE_URL}/agents/chat",
    json={
        "message": "How fast can I lose it safely?",
        "conversation_history": conversation_history
    },
    headers=HEADERS
).json()

conversation_history.append({"role": "user", "content": "How fast can I lose it safely?"})
conversation_history.append({"role": "assistant", "content": response2["response"]})

# Continue conversation...
```

---

## Agent Capabilities Summary

| Agent | Context-Aware | Uses User Data | Multi-turn | Best For |
|-------|--------------|---------------|------------|----------|
| **Daily Summary** | ✅ | ✅ | ❌ | End-of-day insights and progress tracking |
| **Chatbot** | ✅ | ❌ | ✅ | General Q&A, education, motivation |
| **Nutrition Coach** | ✅ | ✅ | ❌ | Personalized nutrition advice and meal planning |
| **Workout Coach** | ✅ | ✅ | ❌ | Training programming and technique advice |

---

## LLM Configuration

All agents use the LLM configuration from `backend/app/config.py`:

```python
# LLM Settings
LLM_PROVIDER: str = "openai"  # or "anthropic", "google"
LLM_MODEL_NAME: str = "gpt-4o"  # or "claude-3-5-sonnet-20241022", "gemini-pro"
LLM_TEMPERATURE: float = 0.7
LLM_MAX_TOKENS: int = 1000
```

**Cost Optimization**:
- Daily Summary: 500-800 tokens (~$0.01 per request with GPT-4)
- Chatbot: 200-500 tokens (~$0.005 per request)
- Nutrition Coach: 800-1200 tokens (~$0.015 per request)
- Workout Coach: 800-1200 tokens (~$0.015 per request)

**Recommendation**: Use `gemini-2.0-flash-exp` for production to reduce costs by ~50x.

---

## Testing

Run integration tests:

```bash
cd backend
pytest tests/test_agents_api.py -v
```

Or run tests manually:

```bash
cd backend
python tests/test_agents_api.py
```

---

## Troubleshooting

### "LLM not configured" Error

**Problem**: Agent returns 500 error with message about LLM configuration.

**Solution**: Ensure environment variables are set:
```bash
# For OpenAI
export OPENAI_API_KEY=your_key_here

# For Anthropic
export ANTHROPIC_API_KEY=your_key_here

# For Google
export GOOGLE_API_KEY=your_key_here
```

### "Agent execution failed" Error

**Problem**: Agent crashes during execution.

**Debug Steps**:
1. Check backend logs for detailed error
2. Verify database connection is working
3. Test LLM API key with a simple request
4. Ensure user has data for context (for coaches)

### Slow Response Times

**Problem**: Agent requests take >10 seconds.

**Optimization**:
1. Use faster models (flash/mini variants)
2. Reduce `LLM_MAX_TOKENS` in config
3. Implement response streaming (future feature)
4. Cache frequently asked questions

---

## Future Enhancements

**Planned Features**:
- [ ] Response streaming for real-time output
- [ ] Agent memory across sessions
- [ ] Multi-agent coordination (agents consulting each other)
- [ ] Voice input/output support
- [ ] Image analysis integration with Vision Agent
- [ ] Personalized training program generation
- [ ] Meal plan generation (7-day plans)
- [ ] Progress prediction and goal timeline estimation

---

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/your-repo/fitcoach/issues
- **Documentation**: See `backend/app/agents/` for agent implementation details
- **Prompts**: See `backend/app/agents/prompts/` to customize agent personalities

---

**Last Updated**: November 7, 2025
**API Version**: v1
**Agents Version**: 1.0
