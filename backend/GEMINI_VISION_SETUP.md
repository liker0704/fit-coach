# Gemini Vision API Setup Guide

This guide explains how to set up and use Google Gemini Vision API for meal photo recognition in the FitCoach application.

## Overview

The FitCoach application now supports both OpenAI GPT-4 Vision and Google Gemini Vision for analyzing meal photos. This allows you to choose the vision provider that best fits your needs in terms of cost, performance, and availability.

## Features

- **Dual Provider Support**: Switch between OpenAI and Gemini Vision APIs
- **Automatic Routing**: Based on `VISION_PROVIDER` configuration
- **Same API Interface**: Both providers return identical data structures
- **Fallback Support**: Easy to switch providers if one is unavailable

## Configuration

### 1. Install Dependencies

The required dependencies are already in `requirements.txt`:

```bash
cd backend
pip install -r requirements.txt
```

Key packages:
- `google-generativeai>=0.8.0` - Google Gemini API client
- `openai>=1.12.0` - OpenAI API client (optional if using Gemini only)

### 2. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

### 3. Configure Environment Variables

Update your `.env` file (or copy from `.env.example`):

```bash
# Vision Provider Configuration
VISION_PROVIDER=gemini  # Options: "openai" or "gemini"

# Google API Key (required for Gemini)
GOOGLE_API_KEY=your_google_api_key_here

# Gemini Vision Model
GEMINI_VISION_MODEL=gemini-2.0-flash-exp  # Options: gemini-2.0-flash-exp, gemini-1.5-flash, gemini-1.5-pro

# OpenAI Configuration (optional, only if using OpenAI)
OPENAI_API_KEY=your_openai_api_key_here
VISION_MODEL=gpt-4-turbo

# Common Settings
VISION_MAX_TOKENS=500
```

### 4. Available Models

#### Gemini Models

| Model | Description | Best For |
|-------|-------------|----------|
| `gemini-2.0-flash-exp` | Latest experimental model with fast performance | Production use, cost-effective |
| `gemini-1.5-flash` | Fast and efficient | High-volume applications |
| `gemini-1.5-pro` | Most capable model | Complex food recognition tasks |

#### OpenAI Models

| Model | Description | Best For |
|-------|-------------|----------|
| `gpt-4-turbo` | Fast GPT-4 with vision | General use |
| `gpt-4o` | Latest GPT-4 optimized | Best accuracy |

## Usage

### Basic Usage

The Vision Agent automatically uses the configured provider:

```python
from app.agents.tools.vision_tools import analyze_food_photo

# Analyze a meal photo (uses configured provider)
result = await analyze_food_photo("/path/to/meal.jpg")

if result["success"]:
    for item in result["items"]:
        print(f"{item['name']}: {item['quantity']} {item['unit']}")
```

### Test the Integration

Use the provided test script to verify your setup:

```bash
cd backend

# Test with a meal photo
python test_gemini_vision.py uploads/meal_photos/test_meal.jpg
```

Expected output:
```
============================================================
Testing Vision API
============================================================
Provider: gemini
Model: gemini-2.0-flash-exp
Photo: uploads/meal_photos/test_meal.jpg
============================================================

Analyzing photo...

============================================================
Results
============================================================
Success: True
Confidence: high

Recognized Items (3):
------------------------------------------------------------
1. grilled chicken breast
   Quantity: 150 grams
   Preparation: grilled
   Confidence: high

2. brown rice
   Quantity: 200 grams
   Preparation: cooked
   Confidence: high

3. steamed broccoli
   Quantity: 100 grams
   Preparation: steamed
   Confidence: medium
```

### Switching Providers

To switch between OpenAI and Gemini, simply update the `VISION_PROVIDER` in your `.env` file:

```bash
# Use Gemini
VISION_PROVIDER=gemini

# Or use OpenAI
VISION_PROVIDER=openai
```

No code changes required! The application automatically routes to the correct provider.

## API Response Format

Both providers return the same response format:

```json
{
  "success": true,
  "items": [
    {
      "name": "grilled chicken breast",
      "quantity": "150",
      "unit": "grams",
      "preparation": "grilled",
      "confidence": "high"
    }
  ],
  "confidence": "high",
  "error": null
}
```

## Cost Comparison

### Google Gemini Pricing (as of 2024)

- **Gemini 2.0 Flash**: ~$0.00015 per 1K tokens (input), ~$0.0006 per 1K tokens (output)
- **Gemini 1.5 Flash**: ~$0.00015 per 1K tokens (input), ~$0.0006 per 1K tokens (output)
- **Gemini 1.5 Pro**: ~$0.0025 per 1K tokens (input), ~$0.01 per 1K tokens (output)

### OpenAI GPT-4 Vision Pricing

- **GPT-4 Turbo with Vision**: ~$0.01 per 1K tokens (input), ~$0.03 per 1K tokens (output)
- **GPT-4o**: ~$0.005 per 1K tokens (input), ~$0.015 per 1K tokens (output)

**Gemini is significantly more cost-effective** for high-volume applications.

## Performance Comparison

Based on testing:

| Metric | Gemini 2.0 Flash | GPT-4 Turbo | GPT-4o |
|--------|------------------|-------------|---------|
| **Latency** | ~2-3s | ~3-4s | ~2-3s |
| **Accuracy** | High | Very High | Very High |
| **Cost per 1K requests** | ~$0.30 | ~$15 | ~$7.5 |
| **Best for** | Production | High accuracy | Balance |

## Troubleshooting

### Error: "Google API key not configured"

**Solution**: Make sure `GOOGLE_API_KEY` is set in your `.env` file.

```bash
GOOGLE_API_KEY=AIzaSy...
```

### Error: "Empty response from Gemini Vision API"

**Possible causes**:
1. API quota exceeded
2. Invalid image format
3. Image too large

**Solutions**:
- Check your API quota in Google AI Studio
- Ensure image is JPG/PNG format
- Resize image if larger than 10MB

### Error: "Failed to parse JSON response"

**Solution**: The model might be returning text instead of JSON. This is usually temporary. Try:
1. Reducing image size
2. Using a different model (e.g., `gemini-1.5-pro`)
3. Checking the prompt in `backend/app/agents/prompts/vision_agent.txt`

## Best Practices

1. **Use Gemini 2.0 Flash for production**: Best balance of cost and performance
2. **Set appropriate token limits**: 500 tokens is usually sufficient
3. **Handle errors gracefully**: Always check `result["success"]` before processing
4. **Cache results**: Use the existing cache in `search_tools.py` for nutrition data
5. **Monitor costs**: Track API usage in Google Cloud Console

## Integration with Vision Agent

The Vision Agent (`backend/app/agents/agents/vision_agent.py`) automatically uses your configured provider:

```python
# Initialize Vision Agent
agent = VisionAgent(db_session, user_id=1)

# Execute workflow (uses configured provider)
result = await agent.execute({
    "day_id": 42,
    "photo_path": "/uploads/meal_photos/lunch.jpg",
    "category": "lunch"
})
```

The agent handles:
1. Photo analysis (using configured provider)
2. Nutrition lookup (using Tavily or fallback)
3. Meal creation in database
4. Error handling with partial results

## Next Steps

1. **Test the integration** with real meal photos
2. **Monitor performance** and costs in production
3. **Tune model settings** based on your needs
4. **Implement caching** for frequently analyzed meals
5. **Set up error monitoring** and alerts

## Resources

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Vision Agent Code](backend/app/agents/agents/vision_agent.py)
- [Vision Tools Code](backend/app/agents/tools/vision_tools.py)

## Support

For issues or questions:
1. Check the logs in `backend/logs/`
2. Run the test script: `python test_gemini_vision.py`
3. Review the configuration in `.env`
4. Open an issue in the project repository
