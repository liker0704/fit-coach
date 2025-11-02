# LLM Integration Progress Tracking

**Status**: 📋 Planned (Architecture documented, not yet implemented)

This document tracks the progress of LLM (Large Language Model) integration into FitCoach for AI-powered health coaching features.

---

## 📊 Overall Progress

| Phase | Status | Progress | Notes |
|-------|--------|----------|-------|
| **1. Architecture & Design** | ✅ Complete | 100% | Documented in ADRs |
| **2. Backend Infrastructure** | ⏳ Not Started | 0% | LangChain setup pending |
| **3. Prompt Engineering** | ⏳ Not Started | 0% | Prompt templates pending |
| **4. API Integration** | ⏳ Not Started | 0% | OpenAI API integration |
| **5. Backend Endpoints** | ⏳ Not Started | 0% | REST API endpoints |
| **6. Frontend Integration** | ⏳ Not Started | 0% | UI components for AI |
| **7. Testing & Optimization** | ⏳ Not Started | 0% | Performance testing |

**Total Progress**: 14% (1/7 phases complete)

---

## 🎯 Planned Features

### Core AI Features

#### 1. Daily Summary Generation ⏳
**Status**: Planned
**Description**: Generate comprehensive daily summaries based on user's tracked data

**Functionality**:
- Analyze meals, exercises, water intake, sleep, and mood
- Provide personalized insights and observations
- Highlight achievements and areas for improvement
- Generate effort score (0-10) based on daily activities

**API Endpoint**: `POST /api/v1/ai/summary/{day_id}`

---

#### 2. Meal Analysis ⏳
**Status**: Planned
**Description**: Analyze individual meals and provide nutritional insights

**Functionality**:
- Evaluate macro/micronutrient balance
- Suggest improvements for better nutrition
- Identify missing nutrients or overconsumption
- Provide context-aware recommendations based on user goals

**API Endpoint**: `POST /api/v1/ai/meal-analysis/{meal_id}`

---

#### 3. Exercise Recommendations ⏳
**Status**: Planned
**Description**: Suggest exercises based on user's history and goals

**Functionality**:
- Analyze workout patterns and progress
- Recommend exercises to balance training
- Suggest intensity levels and durations
- Consider rest days and recovery

**API Endpoint**: `POST /api/v1/ai/exercise-recommendations`

---

#### 4. Weekly/Monthly Insights ⏳
**Status**: Planned
**Description**: Provide aggregated insights over longer periods

**Functionality**:
- Identify trends in health metrics
- Highlight achievements and milestones
- Suggest goals for next period
- Compare progress against previous periods

**API Endpoint**: `POST /api/v1/ai/insights`

---

## 🏗️ Technical Architecture

### Technology Stack (Planned)

| Component | Technology | Purpose |
|-----------|------------|---------|
| LLM Framework | **LangChain** | Prompt management, chains, memory |
| LLM Provider | **OpenAI GPT-3.5/4** | Primary LLM service |
| Fallback Provider | **Google Gemini** | Alternative LLM (optional) |
| Caching | **Redis** | Cache LLM responses for cost optimization |
| Vector DB | **PostgreSQL pgvector** (future) | Semantic search for user history |

### Configuration (from .env)

```env
# LLM Provider
LLM_PROVIDER=openai  # Options: openai, gemini

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL_NAME=gpt-3.5-turbo  # or gpt-4-turbo for better quality
LLM_TEMPERATURE=0.7  # 0.0-1.0 (lower = more deterministic)
LLM_MAX_TOKENS=500  # Maximum tokens in response

# Google Gemini (Optional)
GOOGLE_API_KEY=your_google_api_key_here
# LLM_MODEL_NAME=gemini-pro  # or gemini-1.5-flash
```

---

## 📋 Implementation Roadmap

### Phase 1: Backend Infrastructure (Estimated: 20 hours)

#### ✅ Completed Tasks
- [x] Architecture design and ADR documentation
- [x] Environment configuration (.env setup)

#### ⏳ Pending Tasks

**1.1 LangChain Setup** (4 hours)
- [ ] Install LangChain dependencies (`langchain`, `langchain-openai`)
- [ ] Create `app/services/llm/` directory structure
- [ ] Implement base LLM service class
- [ ] Configure OpenAI provider
- [ ] Configure Gemini provider (optional fallback)
- [ ] Add provider switching logic based on config

**1.2 Prompt Templates** (6 hours)
- [ ] Create `app/services/llm/prompts/` directory
- [ ] Design prompt template for daily summary
- [ ] Design prompt template for meal analysis
- [ ] Design prompt template for exercise recommendations
- [ ] Design prompt template for weekly/monthly insights
- [ ] Implement prompt versioning system

**1.3 LLM Response Handling** (4 hours)
- [ ] Create response parsing utilities
- [ ] Implement error handling for LLM failures
- [ ] Add retry logic with exponential backoff
- [ ] Create response validation schemas (Pydantic)

**1.4 Caching Layer** (4 hours)
- [ ] Implement Redis caching for LLM responses
- [ ] Create cache key generation strategy
- [ ] Set appropriate TTL for different response types
- [ ] Add cache invalidation logic

**1.5 Cost Tracking** (2 hours)
- [ ] Implement token usage tracking
- [ ] Log LLM API costs per request
- [ ] Create monitoring dashboard queries

---

### Phase 2: Backend API Endpoints (Estimated: 15 hours)

**2.1 Daily Summary Endpoint** (4 hours)
- [ ] Create `POST /api/v1/ai/summary/{day_id}` endpoint
- [ ] Fetch day data with all related entities (meals, exercises, etc.)
- [ ] Format data for LLM prompt
- [ ] Generate summary using LLM
- [ ] Store summary in database (new field: `day.ai_summary`)
- [ ] Return formatted response

**2.2 Meal Analysis Endpoint** (3 hours)
- [ ] Create `POST /api/v1/ai/meal-analysis/{meal_id}` endpoint
- [ ] Fetch meal data with nutrients
- [ ] Generate meal insights using LLM
- [ ] Store insights in database (new field: `meal.ai_insights`)
- [ ] Return formatted response

**2.3 Exercise Recommendations Endpoint** (4 hours)
- [ ] Create `POST /api/v1/ai/exercise-recommendations` endpoint
- [ ] Fetch user's exercise history
- [ ] Analyze patterns and progress
- [ ] Generate personalized recommendations
- [ ] Return structured recommendations list

**2.4 Weekly/Monthly Insights Endpoint** (4 hours)
- [ ] Create `POST /api/v1/ai/insights` endpoint
- [ ] Add query parameters for date range
- [ ] Aggregate data over specified period
- [ ] Generate trend analysis using LLM
- [ ] Return insights with visualizable metrics

---

### Phase 3: Database Schema Updates (Estimated: 4 hours)

**3.1 Add AI-related Fields** (2 hours)
- [ ] Add `ai_summary: TEXT` to `days` table
- [ ] Add `ai_insights: TEXT` to `meals` table
- [ ] Add `effort_score: INTEGER` (0-10) to `days` table
- [ ] Create Alembic migration

**3.2 Add LLM Usage Tracking Table** (2 hours)
- [ ] Create `llm_requests` table (id, user_id, endpoint, tokens, cost, created_at)
- [ ] Create Alembic migration
- [ ] Implement tracking in LLM service

---

### Phase 4: Frontend Integration (Estimated: 16 hours)

**4.1 Desktop: Daily Summary UI** (4 hours)
- [ ] Create `AISummaryCard` component
- [ ] Add "Generate Summary" button to DayView
- [ ] Display loading state during generation
- [ ] Show generated summary with formatting
- [ ] Add regenerate functionality

**4.2 Desktop: Meal Insights UI** (3 hours)
- [ ] Add "Get Insights" button to meal cards
- [ ] Create `MealInsightsDialog` component
- [ ] Display nutritional analysis
- [ ] Show recommendations

**4.3 Desktop: Exercise Recommendations UI** (4 hours)
- [ ] Create `ExerciseRecommendations` page
- [ ] Add recommendation cards with exercise details
- [ ] Implement "Add to Day" functionality
- [ ] Show reasoning for each recommendation

**4.4 Desktop: Weekly Insights UI** (3 hours)
- [ ] Create `InsightsView` in Statistics page
- [ ] Add date range selector
- [ ] Display trends and achievements
- [ ] Show goal suggestions

**4.5 iOS: AI Features** (2 hours - basic implementation)
- [ ] Mirror desktop functionality in iOS app
- [ ] Adapt UI to iOS native components

---

### Phase 5: Testing & Optimization (Estimated: 10 hours)

**5.1 Unit Tests** (4 hours)
- [ ] Test LLM service with mocked responses
- [ ] Test prompt template rendering
- [ ] Test response parsing logic
- [ ] Test caching layer

**5.2 Integration Tests** (3 hours)
- [ ] Test API endpoints end-to-end
- [ ] Test with real OpenAI API (dev environment)
- [ ] Verify database updates
- [ ] Test error handling scenarios

**5.3 Performance Optimization** (3 hours)
- [ ] Measure response times
- [ ] Optimize prompt lengths
- [ ] Tune caching TTL values
- [ ] Implement request batching (if needed)

---

## 💰 Cost Estimation

### OpenAI API Pricing (as of 2025)

**GPT-3.5-turbo**:
- Input: $0.0015 / 1K tokens
- Output: $0.002 / 1K tokens

**GPT-4-turbo**:
- Input: $0.01 / 1K tokens
- Output: $0.03 / 1K tokens

### Estimated Usage per User per Day

| Feature | Avg Tokens | Cost (GPT-3.5) | Cost (GPT-4) | Frequency |
|---------|------------|----------------|--------------|-----------|
| Daily Summary | 800 | $0.0024 | $0.024 | 1x/day |
| Meal Analysis | 400 | $0.0012 | $0.012 | 3x/day |
| Exercise Rec | 600 | $0.0018 | $0.018 | 1x/week |
| Weekly Insights | 1200 | $0.0036 | $0.036 | 1x/week |

**Daily Cost per User**:
- GPT-3.5: ~$0.006/day = **$1.80/month**
- GPT-4: ~$0.06/day = **$18/month**

**Recommendation**: Start with GPT-3.5-turbo, upgrade to GPT-4 only for premium users.

---

## 🚧 Current Blockers

None - waiting for implementation to begin.

---

## 🎯 Success Metrics

### Quality Metrics
- [ ] User satisfaction rating > 4.0/5.0 for AI features
- [ ] Summary accuracy (human evaluation) > 85%
- [ ] Recommendation acceptance rate > 40%

### Performance Metrics
- [ ] Response time < 5s (p95)
- [ ] Cache hit rate > 60%
- [ ] API success rate > 99%

### Cost Metrics
- [ ] Monthly cost per active user < $2 (GPT-3.5)
- [ ] Token usage within budget limits

---

## 📚 References

- [LangChain Documentation](https://docs.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google Gemini API](https://ai.google.dev/)
- [Architecture Decisions](./architecture-decisions.md) - ADR #11: LLM Integration

---

## 🔄 Updates Log

| Date | Update | Author |
|------|--------|--------|
| 2025-11-02 | Initial progress tracking document created | System |
| TBD | LangChain setup complete | TBD |
| TBD | First AI summary generated | TBD |

---

**Last Updated**: 2025-11-02
**Next Review**: After backend MVP completion

**Note**: This is a living document. Update progress as implementation advances.
