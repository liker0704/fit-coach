# Weight Tracking Feature

## Overview

Daily weight tracking feature allows users to record their weight for each day and visualize weight trends over time through the Statistics page.

**Status:** ✅ Completed
**Version:** Added in commit `1d1b28d`
**Date:** November 8, 2025

---

## Backend Implementation

### 1. Database Schema

#### Day Model (`backend/app/models/day.py`)

Added optional `weight` column to the `days` table:

```python
# Line 38
weight = Column(Numeric(5, 2))  # kg, optional daily weight measurement
```

**Specifications:**
- Type: `Numeric(5, 2)` - supports values like 75.50 kg
- Nullable: `True` - weight is optional for each day
- Range: 1-500 kg (validated at schema level)
- Precision: 2 decimal places

### 2. Pydantic Schemas

#### Updated Schemas (`backend/app/schemas/day.py`)

Added `weight` field to all Day schemas with validation:

```python
# DayBase, DayCreate, DayUpdate
weight: Optional[Decimal] = Field(None, gt=0, le=500)
```

**Validation Rules:**
- Must be greater than 0 kg
- Must not exceed 500 kg
- Optional field (can be null)
- Automatically included in API responses (DayResponse)

### 3. Database Migration

#### Migration File
`backend/alembic/versions/0df93e546a3f_add_weight_to_days.py`

**Upgrade:**
```python
op.add_column('days', sa.Column('weight', sa.Numeric(precision=5, scale=2), nullable=True))
```

**Downgrade:**
```python
op.drop_column('days', 'weight')
```

**To apply migration:**
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

---

## Frontend Implementation

### 1. TypeScript Types

#### Day Interface (`desktop/src/types/models/health.ts`)

```typescript
export interface Day {
  // ... existing fields
  weight?: number | null;  // Line 8
  // ... rest of fields
}
```

### 2. API Service

#### Day Service (`desktop/src/services/modules/dayService.ts`)

Added `updateDay()` method to support partial updates:

```typescript
updateDay: async (
  dayId: number,
  data: Partial<Pick<Day, 'tag' | 'feeling' | 'effort_score' | 'weight' | 'summary'>>
): Promise<Day> => {
  const response = await apiClient.put(`/days/${dayId}`, data);
  return response.data;
}
```

### 3. User Interface

#### DayView Component (`desktop/src/pages/calendar/DayView.tsx`)

**Location:** Lines 116-140 (header section)

**Features:**
- Inline weight input in day header
- Auto-save on blur or Enter key
- Validation (1-500 kg range)
- Loading state during save
- Toast notifications for feedback
- Scale icon for visual identification

**Implementation:**
```typescript
// State management
const [weightInput, setWeightInput] = useState<string>('');
const [isUpdatingWeight, setIsUpdatingWeight] = useState(false);

// Auto-save handler
const handleWeightSave = async () => {
  const weight = parseFloat(weightInput);
  if (isNaN(weight) || weight <= 0 || weight > 500) {
    toast({ title: 'Invalid Weight', variant: 'destructive' });
    return;
  }
  await dayService.updateDay(Number(dayId), { weight });
  toast({ title: 'Success', description: 'Weight updated successfully' });
};
```

### 4. Weight Chart

#### WeightChart Component (`desktop/src/components/stats/WeightChart.tsx`)

**Location:** Statistics page, first chart

**Previous Implementation:**
- Hardcoded placeholder data (75 kg for all days)
- Static Y-axis domain [60, 80]

**New Implementation:**
- Extracts real weight data from days
- Filters days with `weight != null`
- Dynamic Y-axis domain based on actual data
- Empty state when no weight data exists
- Visual dots on data points

**Code Changes:**
```typescript
// Line 25-34: Data transformation
const data = useMemo(
  () =>
    days
      .filter((day) => day.weight != null)  // Only days with weight
      .map((day) => ({
        date: format(new Date(day.date), 'MM/dd'),
        weight: Number(day.weight),
      })),
  [days]
);

// Line 36-41: Dynamic Y-axis
const weights = data.map((d) => d.weight);
const minWeight = weights.length > 0 ? Math.min(...weights) : 60;
const maxWeight = weights.length > 0 ? Math.max(...weights) : 80;
const padding = 5;
const yDomain = [Math.max(0, minWeight - padding), maxWeight + padding];
```

**Empty State:**
```tsx
{data.length === 0 ? (
  <div className="flex items-center justify-center h-[300px]">
    <p>No weight data recorded yet. Add weight in the daily view to see your trend.</p>
  </div>
) : (
  <LineChart data={data} yDomain={yDomain}>
    {/* Chart components */}
  </LineChart>
)}
```

---

## User Workflow

### Recording Weight

1. User opens a day from Calendar
2. In DayView header, sees "Weight (kg)" input field
3. Enters weight value (e.g., 72.5)
4. Presses Enter or clicks outside input
5. Weight auto-saves to backend
6. Toast notification confirms success

### Viewing Weight Trend

1. User navigates to Statistics page
2. First chart "Weight Trend" displays line graph
3. X-axis shows dates (MM/DD format)
4. Y-axis shows weight in kg (auto-scaled)
5. Trend line connects all recorded weights
6. If no data: shows helpful empty state message

---

## API Endpoints

### Get Day (includes weight)
```
GET /api/v1/days/id/{day_id}

Response:
{
  "id": 1,
  "date": "2024-11-08",
  "weight": 75.5,
  // ... other fields
}
```

### Update Day (partial update)
```
PUT /api/v1/days/{day_id}

Request Body:
{
  "weight": 72.0
}

Response: Updated Day object
```

---

## Validation & Error Handling

### Backend Validation
- Pydantic schema enforces `gt=0, le=500`
- Returns 422 Unprocessable Entity for invalid values
- Examples:
  - ✅ Valid: 1.0, 50.5, 100.0, 500.0
  - ❌ Invalid: 0, -5, 600

### Frontend Validation
- Input type: `number` with min/max attributes
- Client-side check before API call
- User-friendly error messages
- Prevents unnecessary API calls

### Error Scenarios

**Scenario 1: Invalid weight value**
```typescript
// User enters 0 or negative
→ Toast: "Invalid Weight: Please enter a valid weight between 1 and 500 kg"
→ Value not saved
```

**Scenario 2: Network error**
```typescript
// API call fails
→ Toast: "Error: Failed to update weight"
→ User can retry
```

---

## Testing

### Manual Testing Checklist

- [ ] Enter valid weight (e.g., 72.5) → Saves successfully
- [ ] Enter boundary values (1.0, 500.0) → Accepts both
- [ ] Enter invalid values (0, -5, 600) → Shows validation error
- [ ] Leave weight empty → Saves as null (optional field)
- [ ] Check Statistics page → Weight trend displays correctly
- [ ] Record weights for multiple days → Line graph shows trend
- [ ] No weight data → Empty state displays with helpful message

### Backend Tests

All existing Day model tests pass with new weight field.

**To run backend tests:**
```bash
cd backend
source venv/bin/activate
pytest tests/ -v -k "day"
```

---

## Database Queries

### Get weight trend for date range
```sql
SELECT date, weight
FROM days
WHERE user_id = :user_id
  AND weight IS NOT NULL
  AND date BETWEEN :start_date AND :end_date
ORDER BY date ASC;
```

### Check if user has weight data
```sql
SELECT COUNT(*)
FROM days
WHERE user_id = :user_id
  AND weight IS NOT NULL;
```

---

## Future Enhancements

Potential improvements for future versions:

1. **Target Weight Line**
   - Add reference line on chart showing target weight from user profile
   - Visual goal tracking

2. **Weight Change Indicator**
   - Show +/- kg change from previous weight entry
   - Weekly/monthly weight change summary

3. **BMI Calculation**
   - Auto-calculate BMI using height from profile + daily weight
   - BMI trend chart

4. **Weight Goals**
   - Set weight loss/gain goals with target dates
   - Progress percentage visualization

5. **Export Weight Data**
   - CSV export for weight history
   - Integration with health apps (Apple Health, Google Fit)

---

## Related Files

### Backend
- `backend/app/models/day.py` - Day model with weight column
- `backend/app/schemas/day.py` - Day schemas with weight validation
- `backend/alembic/versions/0df93e546a3f_add_weight_to_days.py` - Migration

### Frontend
- `desktop/src/types/models/health.ts` - TypeScript Day interface
- `desktop/src/services/modules/dayService.ts` - API service with updateDay
- `desktop/src/pages/calendar/DayView.tsx` - Weight input UI
- `desktop/src/components/stats/WeightChart.tsx` - Weight trend visualization

### Git
- **Commit:** `1d1b28d` - feat: implement daily weight tracking in Day model
- **Branch:** `claude/vision-agent-api-mvp-011CUtnYH1RZ2qCVJzP2ALff`
