# Quick Start Guide - Notifications & Voice API Tests

## Created Files

1. **test_notifications_api.py** (24KB, 640 lines)
   - 20 comprehensive tests
   - 6 test classes
   - Full CRUD coverage

2. **test_voice_api.py** (33KB, 969 lines)
   - 31 comprehensive tests
   - 6 test classes
   - STT, TTS, Streaming coverage

3. **conftest.py** (748 bytes)
   - Shared pytest fixtures
   - Custom markers

4. **TEST_COVERAGE_REPORT.md** (8.4KB)
   - Detailed documentation
   - All test descriptions
   - Running instructions

## Quick Run Commands

```bash
# Start backend server first (required)
cd /home/user/fit-coach/backend
uvicorn app.main:app --host 0.0.0.0 --port 8001

# In another terminal, run tests:

# Run all new tests
pytest tests/test_notifications_api.py tests/test_voice_api.py -v

# Run notifications only
pytest tests/test_notifications_api.py -v

# Run voice API only
pytest tests/test_voice_api.py -v

# Run with detailed output
pytest tests/test_notifications_api.py tests/test_voice_api.py -v -s

# Run specific test class
pytest tests/test_notifications_api.py::TestNotificationsCRUD -v
pytest tests/test_voice_api.py::TestSpeechToText -v
```

## Test Coverage Summary

### Notifications API (20 tests)
- ✅ List notifications (all & unread)
- ✅ Get notification by ID
- ✅ Mark as read
- ✅ Delete notification
- ✅ Authorization checks
- ✅ Different notification types
- ✅ JSON data handling
- ✅ Edge cases

### Voice API (31 tests)
- ✅ Speech-to-Text (8 tests)
  - Multiple languages
  - Multiple formats
  - Error handling

- ✅ Text-to-Speech (11 tests)
  - 6 voice options
  - Speed control
  - Unicode support

- ✅ TTS Audio endpoint (3 tests)
- ✅ TTS Streaming (3 tests)
- ✅ Edge cases (5 tests)
- ✅ Configuration (1 test)

## Test Features

- ✅ **Authentication**: All endpoints require auth
- ✅ **Authorization**: Cross-user protection
- ✅ **Mocking**: OpenAI API mocked (no real calls)
- ✅ **Validation**: Input validation tested
- ✅ **Error Handling**: 400, 403, 404, 500 responses
- ✅ **Edge Cases**: Large files, long text, concurrent requests

## Dependencies

```bash
pip install pytest pytest-asyncio httpx
```

## Notes

- Tests use mocked OpenAI API (no API key needed)
- Each test file creates unique test user
- Tests require backend server running on port 8001
- Database state is modified (test data created)

## File Locations

```
/home/user/fit-coach/backend/tests/
├── test_notifications_api.py   # Notifications tests
├── test_voice_api.py            # Voice API tests
├── conftest.py                  # Shared fixtures
├── TEST_COVERAGE_REPORT.md      # Detailed docs
└── QUICK_START.md               # This file
```

## Expected Results

All 51 tests should pass if:
- Backend server is running
- Database is accessible
- No port conflicts

**Total Test Count: 51 tests**
**Total Lines: 1,609 lines**
**Status: Ready to Run ✅**
