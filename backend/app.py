from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import httpx
import base64
from dotenv import load_dotenv
from chatbot import ArtGalleryChatbot

# Load environment variables
load_dotenv()

app = FastAPI(title="Art Gallery Chatbot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("WARNING: GEMINI_API_KEY not set. Please add it to .env file")
    chatbot = None
else:
    chatbot = ArtGalleryChatbot(API_KEY)

# Request/Response models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    type: str
    message: str
    artworks: Optional[List[Dict[str, Any]]] = None
    filters: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {
        "message": "Art Gallery Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "POST - Send chat messages",
            "/greeting": "GET - Get initial greeting",
            "/filters": "GET - Get available filters"
        }
    }

@app.get("/greeting")
async def get_greeting():
    """Get initial greeting message"""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized. Please set GEMINI_API_KEY")

    return {
        "message": chatbot.get_greeting()
    }

@app.get("/filters")
async def get_filters():
    """Get available filter options"""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")

    return chatbot.available_filters

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message"""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized. Please set GEMINI_API_KEY in .env file")

    try:
        # Convert to dict format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Get response from chatbot
        response = chatbot.chat(messages)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "chatbot_initialized": chatbot is not None
    }

@app.get("/proxy-image")
async def proxy_image(url: str):
    """Proxy image requests to avoid CORS issues"""
    try:
        # Set up headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.metmuseum.org/',
            'Connection': 'keep-alive',
        }

        async with httpx.AsyncClient(
            timeout=60.0,  # Increased timeout
            follow_redirects=True,  # Follow redirects
            verify=True,  # Verify SSL certificates
            headers=headers
        ) as client:
            # Fetch the image
            response = await client.get(url)
            response.raise_for_status()

            # Convert to base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')

            # Determine content type
            content_type = response.headers.get('content-type', 'image/jpeg')

            # If content type is not image, try to guess from URL
            if not content_type.startswith('image/'):
                if url.endswith('.jpg') or url.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif url.endswith('.png'):
                    content_type = 'image/png'
                elif url.endswith('.webp'):
                    content_type = 'image/webp'
                else:
                    content_type = 'image/jpeg'  # Default to JPEG

            # Return as data URL
            data_url = f"data:{content_type};base64,{image_base64}"

            return {
                "success": True,
                "data_url": data_url,
                "content_type": content_type
            }
    except httpx.TimeoutException as e:
        raise HTTPException(status_code=504, detail=f"Image request timed out: {str(e)}")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
