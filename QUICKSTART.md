# Quick Start Guide - Art Gallery Conversational AI Chatbot POC

## 🎯 What is This?

A working POC (Proof of Concept) for an AI-powered chatbot that helps users discover artworks through natural conversation. Built with:
- **Google Gemini AI** (free tier)
- **FastAPI** backend
- **Vanilla JavaScript** frontend
- **40 real artworks** from The Met Museum

---

## 🚀 How to Run

### Method 1: Using the start script (Recommended)

```bash
cd art-gallery-chatbot
./start.sh
```

### Method 2: Manual steps

```bash
# 1. Activate virtual environment
cd art-gallery-chatbot
source venv/bin/activate

# 2. Start backend
cd backend
python app.py

# 3. In another terminal, open frontend
cd frontend
open index.html
# Or serve it: python -m http.server 3000
```

---

## 📋 Requirements Met

### ✅ Data Requirements
- **40 real artworks** with high-quality images from The Met Museum
- **Complete metadata** for each artwork:
  - Title, artist, period
  - Style tags (abstract, landscape, portrait, etc.)
  - Color palette (red, blue, multicolor, etc.)
  - Mood tags (bold, serene, energetic, etc.)
  - Price in INR (₹70,000 - ₹480,000)
  - Dimensions, medium, availability

### ✅ Input/Workflow Design
- **System Prompt**: Guides AI to be an art gallery assistant
- **Conversation Flow**: 2-4 turns to gather:
  1. Style preference (abstract/classical/landscape)
  2. Color preference
  3. Mood
  4. Budget range
- **Stopping Point**: After gathering 2-3 preferences OR when user explicitly asks
- **AI Model**: Google Gemini 2.5 Flash (free, fast, powerful)

### ✅ Technical Stack
- **Backend**: FastAPI (async, lightweight)
- **AI**: Gemini 2.5 Flash via REST API
- **Frontend**: Vanilla JS (no frameworks - fast and simple)
- **Data**: JSON file (easy to replace with MySQL later)
- **Total Files**: 8 core files (minimalist!)

---

## 🎨 Sample Conversation Flow

```
Bot: "Hello! I'm here to help you discover the perfect artwork.
      What kind of art are you looking for today?"

User: "I want something bold and modern for my living room"

Bot: "That sounds exciting! Are you leaning more towards fine-art,
      or perhaps a landscape or portrait?"

User: "Abstract art with red colors"

Bot: "Perfect! What's your budget range?"

User: "Under 2 lakhs"

Bot: "Let me find the perfect artworks for you!"
     [Shows 5 matching artworks with images and details]
```

---

## 📁 Project Structure

```
art-gallery-chatbot/
├── backend/
│   ├── app.py              # FastAPI server (main entry)
│   ├── chatbot.py          # Gemini AI integration
│   ├── recommender.py      # Artwork recommendation engine
│   └── fetch_artworks.py   # Met Museum data fetcher
├── data/
│   └── artworks.json       # 40 artworks with metadata
├── frontend/
│   ├── index.html          # Chat UI
│   └── script.js           # Frontend logic
├── venv/                   # Virtual environment
├── .env                    # API key (GEMINI_API_KEY)
├── requirements.txt        # Python dependencies
├── start.sh                # Quick start script
└── README.md               # Full documentation
```

---

## 🔑 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/greeting` | GET | Get initial greeting |
| `/filters` | GET | Available filters (styles, colors, moods) |
| `/chat` | POST | Send chat message |
| `/health` | GET | Health check |

---

## 💡 Key Features

### 1. Intelligent Conversation
- Understands natural language ("bold red abstract under ₹2L")
- Asks clarifying questions
- Keeps conversation concise (2-3 sentences per response)

### 2. Smart Recommendations
- **Filters artworks** by style, color, mood, budget
- **Scores matches** based on preference alignment
- **Returns top 5** best matches with reasoning

### 3. Rich Artwork Display
- High-resolution images
- Complete metadata (artist, price, dimensions)
- Visual tags for styles, colors, moods
- Clickable images to view full size

### 4. Minimalist & Fast
- No heavy frameworks
- Direct REST API calls (no SDK overhead)
- JSON-based data (fast queries)
- Async backend (handles multiple users)

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
GEMINI_API_KEY=your_api_key_here
```

Get your free API key: https://makersuite.google.com/app/apikey

### System Prompt (backend/chatbot.py)

Easily customizable to change:
- Conversation style
- Number of turns before recommendation
- Available filter options
- Response format

---

## 📊 Cost Analysis

### Free Tier Limits (Gemini)
- **60 requests per minute**
- **1500 requests per day**
- Perfect for POC and testing!

### Estimated Costs for Production
- Average conversation: 3-4 API calls
- 1000 conversations/day = ~3000 API calls
- **Cost**: FREE (within limits) or ~₹400-800/month if scaled

---

## 🎯 Next Steps for Production

1. **Replace Data**: Use client's actual 1,800 artworks
2. **Add Database**: Switch from JSON to MySQL
3. **User Sessions**: Track conversation history
4. **Analytics**: Log popular styles, price ranges
5. **Image Upload**: Phase 2 feature (room photo matching)
6. **Admin Panel**: Bulk edit artwork metadata
7. **Deploy**: AWS/GCP/Azure with CDN

---

## ⚠️ Important Notes

1. **API Key Security**: Never commit .env to git
2. **Rate Limits**: Free tier has 60 req/min limit
3. **Python Version**: Works with Python 3.8+
4. **CORS**: Currently allows all origins (tighten for production)
5. **Error Handling**: Basic error handling (enhance for production)

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>
```

### "Chatbot not initialized" error
```bash
# Ensure .env file exists with API key
cat .env

# Should show:
# GEMINI_API_KEY=your_key_here
```

### Frontend can't connect
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify API_URL in frontend/script.js

---

## 📝 Testing Commands

```bash
# Health check
curl http://localhost:8000/health

# Get greeting
curl http://localhost:8000/greeting

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"I want bold art"}]}'
```

---

## 🎉 Success Criteria

✅ Real artwork images and metadata
✅ Natural conversational flow
✅ Smart recommendations based on preferences
✅ Fast response times (< 3 seconds)
✅ Beautiful, responsive UI
✅ Minimalist codebase (8 core files)
✅ Free tier AI (Gemini)
✅ Ready to demo

---

## 📞 Support

For issues or questions:
1. Check QUICKSTART.md (this file)
2. Check README.md for detailed documentation
3. Check server logs in terminal
4. Verify .env file has correct API key

---

**POC Created**: November 2025
**Time to Build**: ~30 minutes
**Status**: ✅ Ready for Demo
