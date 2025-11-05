# Art Gallery Conversational AI Chatbot - POC

A minimalist proof-of-concept for an AI-powered chatbot that helps users discover artworks through natural conversation.

## Features

- Natural conversational interface using Claude AI
- Intelligent artwork recommendations based on:
  - Style preferences (abstract, classical, landscape, etc.)
  - Color preferences
  - Mood/feeling
  - Budget constraints
- Real artwork data from The Met Museum (40 curated pieces)
- Fast and efficient conversation flow (2-4 turns)
- Beautiful, responsive UI

## Tech Stack

**Backend:**
- Python 3.8+
- FastAPI (lightweight, async API)
- Anthropic Claude API (conversational AI)
- Simple JSON-based data storage

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- No frameworks - pure and fast

## Project Structure

```
art-gallery-chatbot/
├── backend/
│   ├── app.py              # FastAPI server
│   ├── chatbot.py          # Conversational AI logic
│   ├── recommender.py      # Recommendation engine
│   └── fetch_artworks.py   # Data fetching script
├── data/
│   └── artworks.json       # Artwork metadata (40 pieces)
├── frontend/
│   ├── index.html          # Chat UI
│   └── script.js           # Frontend logic
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
└── README.md
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd art-gallery-chatbot
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Get your API key from: https://console.anthropic.com/

### 3. Start Backend Server

```bash
cd backend
python app.py
```

Server will start at: `http://localhost:8000`

### 4. Open Frontend

Open `frontend/index.html` in your browser, or use a simple HTTP server:

```bash
cd frontend
python -m http.server 3000
```

Then visit: `http://localhost:3000`

## How It Works

### Conversation Flow

1. **Greeting**: Bot asks about style preferences
2. **Color Preference**: Extracts favorite colors
3. **Budget**: Gets price range
4. **Recommendation**: Shows 3-5 matching artworks

### AI Logic

- Uses Claude 3.5 Sonnet for natural conversation
- Extracts structured filters from unstructured chat
- Scores artworks based on match quality
- Generates personalized descriptions

### When to Recommend

- After 2-3 conversational turns
- Once we have: Style + Color + Budget
- If user explicitly asks ("show me", "recommend")

## API Endpoints

- `GET /` - API info
- `GET /greeting` - Get initial greeting
- `GET /filters` - Get available filter options
- `POST /chat` - Send chat message
- `GET /health` - Health check

## Data Schema

Each artwork has:

```json
{
  "id": "unique_id",
  "title": "Artwork Title",
  "artist": "Artist Name",
  "price": 150000,
  "currency": "INR",
  "style": ["abstract", "contemporary"],
  "colors": ["red", "black"],
  "medium": "oil on canvas",
  "mood": ["bold", "energetic"],
  "dimensions": "48x36 inches",
  "availability": "available",
  "image_url": "https://...",
  "description": "..."
}
```

## Cost Estimate

- **Claude 3.5 Sonnet**: ~₹0.25 per conversation (3-4 turns)
- **Expected**: ₹400-800 for 1000 test conversations

## Next Steps for Production

1. Replace Met Museum data with actual gallery inventory
2. Add user authentication
3. Implement session management
4. Add image upload for visual search
5. Deploy to cloud (AWS/GCP/Azure)
6. Add analytics tracking
7. Implement feedback mechanism

## Sample Conversation

```
Bot: "Hello! I'm here to help you discover the perfect artwork.
      What kind of art are you looking for today?"

User: "I want something bold and modern for my living room"

Bot: "Great choice! Do you have any color preferences in mind?"

User: "I love red and black"

Bot: "Perfect! What's your budget range?"

User: "Under 2 lakhs"

Bot: "Let me find the perfect artworks for you!"
     [Shows 5 matching artworks with images and details]
```

## Troubleshooting

**Backend won't start:**
- Check if port 8000 is available
- Ensure ANTHROPIC_API_KEY is set in .env

**Frontend can't connect:**
- Make sure backend is running
- Check CORS settings in app.py
- Verify API_URL in script.js matches backend URL

**No recommendations:**
- Check if artworks.json exists and has data
- Verify filters in conversation are being extracted
- Look at backend logs for errors

## License

MIT License - Free to use for POC and development
