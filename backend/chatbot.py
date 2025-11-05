import json
import requests
from typing import List, Dict, Any
from recommender import ArtworkRecommender

class ArtGalleryChatbot:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
        self.recommender = ArtworkRecommender()
        self.available_filters = self.recommender.get_available_filters()

        # System prompt
        self.system_prompt = f"""You are an art gallery assistant helping buyers discover artwork through natural conversation.

Your role:
1. Have a brief, friendly conversation (2-4 turns) to understand preferences
2. Extract: style, colors, mood, and budget
3. Once you have enough info (at least 2-3 preferences), recommend artworks

Guidelines:
- Be conversational but concise (2-3 sentences max)
- Ask one preference at a time
- If user is vague, suggest popular options
- After gathering preferences, say "Let me find perfect pieces for you!"

Available options:
- Styles: {', '.join(self.available_filters['styles'])}
- Colors: {', '.join(self.available_filters['colors'])}
- Moods: {', '.join(self.available_filters['moods'])}

When ready to recommend, respond with JSON ONLY (no additional text):
{{"action": "recommend", "filters": {{"style": "...", "colors": ["..."], "mood": "...", "max_price": 200000}}}}

Otherwise, continue conversation naturally."""

    def call_gemini(self, prompt: str) -> str:
        """Call Gemini API directly via REST"""
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        try:
            response = requests.post(self.api_url, json=payload, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            data = response.json()

            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                return "I apologize, but I couldn't process that. Could you rephrase?"

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return "I'm having trouble connecting. Please try again."

    def extract_intent(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation and extract user intent/preferences"""

        # Build conversation context with system prompt
        conversation_parts = [self.system_prompt, ""]

        for msg in messages:
            role = "User" if msg['role'] == 'user' else "Assistant"
            conversation_parts.append(f"{role}: {msg['content']}")

        # Add instruction for next response
        conversation_parts.append("\nAssistant:")

        full_prompt = "\n".join(conversation_parts)

        # Generate response
        assistant_message = self.call_gemini(full_prompt)

        # Check if it's time to recommend
        if '"action": "recommend"' in assistant_message or '{"action": "recommend"' in assistant_message:
            try:
                # Extract JSON from response
                json_start = assistant_message.find('{')
                json_end = assistant_message.rfind('}') + 1
                json_str = assistant_message[json_start:json_end]
                data = json.loads(json_str)

                return {
                    'action': 'recommend',
                    'filters': data.get('filters', {}),
                    'message': "Let me find the perfect artworks for you!"
                }
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                print(f"Response: {assistant_message}")
                pass

        return {
            'action': 'continue',
            'message': assistant_message
        }

    def format_artwork_response(self, artworks: List[Dict], filters: Dict) -> str:
        """Format artwork recommendations as conversational response"""

        if not artworks:
            return "I couldn't find exact matches, but let me show you some beautiful pieces you might love!"

        response = f"Based on your preferences, I found {len(artworks)} stunning pieces:\n\n"

        for i, art in enumerate(artworks, 1):
            price_str = f"₹{art['price']:,}"
            response += f"{i}. **{art['title']}**\n"
            if art['artist']:
                response += f"   Artist: {art['artist']}\n"
            response += f"   Style: {', '.join(art['style'])}\n"
            response += f"   Colors: {', '.join(art['colors'])}\n"
            response += f"   Mood: {', '.join(art['mood'])}\n"
            response += f"   Price: {price_str}\n"
            response += f"   [View Image]({art['image_url']})\n\n"

        response += "Would you like to know more about any of these pieces?"
        return response

    def chat(self, messages: List[Dict]) -> Dict[str, Any]:
        """Process chat message and return response"""

        # Extract intent
        intent = self.extract_intent(messages)

        if intent['action'] == 'recommend':
            # Get recommendations
            artworks = self.recommender.recommend(intent['filters'], limit=5)

            return {
                'type': 'recommendation',
                'message': self.format_artwork_response(artworks, intent['filters']),
                'artworks': artworks,
                'filters': intent['filters']
            }
        else:
            return {
                'type': 'conversation',
                'message': intent['message']
            }

    def get_greeting(self) -> str:
        """Initial greeting message"""
        return "Hello! I'm here to help you discover the perfect artwork. What kind of art are you looking for today? For example, do you prefer abstract, classical, or landscape pieces?"
