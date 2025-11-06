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

        # Get price range
        price_range = self.available_filters.get('price_range', {})
        min_lakhs = price_range.get('min_lakhs', 2.5)
        max_lakhs = price_range.get('max_lakhs', 4.9)

        # System prompt
        self.system_prompt = f"""You are an art gallery assistant helping buyers discover artwork through natural conversation.

Your role:
1. Have a brief conversation (2-3 turns max) to understand preferences
2. Extract: style, colors, mood, and budget
3. Ask about preferences BEFORE recommending, unless user explicitly says "anything/any"

CRITICAL RULES FOR WHEN TO RECOMMEND:

**Recommend IMMEDIATELY (no questions) if:**
- User says "anything", "any", "I'm okay with anything", "show me anything"
- User says "give me any image/artwork/painting"
- User explicitly asks to see artworks without specifying preferences

**ASK for preferences FIRST if:**
- User only mentions budget (e.g., "under 2 lakhs") → Ask about style/color/mood preferences
- User mentions only 1-2 criteria → Ask about the missing ones
- First message from user → Always ask what they're looking for

**After asking 1-2 questions:**
- If user still says "anything" or "any" → RECOMMEND IMMEDIATELY
- If user provides preferences → RECOMMEND with those preferences
- Maximum 3 conversational turns before recommending

BUDGET EXTRACTION (IMPORTANT):
- "under 1 lakh" or "under 100000" → max_price: 100000
- "under 2 lakhs" or "under 200000" → max_price: 200000
- "under 3 lakhs" or "under 300000" → max_price: 300000
- "under 4 lakhs" or "under 400000" → max_price: 400000
- "under 5 lakhs" or "under 500000" → max_price: 500000
- If no budget mentioned → max_price: 500000

**IMPORTANT - When asking about budget:**
Always mention our price range in the question. Use this format:
"Do you have a budget in mind? (We have artworks ranging from ₹{min_lakhs} lakhs to ₹{max_lakhs} lakhs)"

Available options:
- Styles: {', '.join(self.available_filters['styles'])}
- Colors: {', '.join(self.available_filters['colors'])}
- Moods: {', '.join(self.available_filters['moods'])}
- Price Range: ₹{min_lakhs} lakhs to ₹{max_lakhs} lakhs

When ready to recommend, respond with JSON ONLY (no additional text):
{{"action": "recommend", "filters": {{"max_price": 200000, "style": "classical", "colors": ["blue"]}}}}

Otherwise, continue conversation naturally and ask about preferences."""

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
            # Build a more specific apology message
            criteria = []
            if filters.get('max_price'):
                criteria.append(f"under ₹{filters['max_price']:,}")
            if filters.get('style'):
                criteria.append(f"{filters['style']} style")
            if filters.get('colors'):
                criteria.append(f"{', '.join(filters['colors'])} colors")
            if filters.get('mood'):
                criteria.append(f"{filters['mood']} mood")

            if criteria:
                criteria_str = " with ".join(criteria)

                # Check if we have items matching partial criteria
                # Try without mood/color filters
                relaxed_filters = {'max_price': filters.get('max_price', 500000)}
                if filters.get('style'):
                    relaxed_filters['style'] = filters['style']

                relaxed_results = self.recommender.filter_artworks(relaxed_filters)

                if relaxed_results:
                    return f"I couldn't find artworks with all your preferences ({criteria_str}). Would you like to see artworks that match some of your criteria, or would you like to adjust your preferences?"
                elif 'max_price' in filters:
                    min_price = min(art['price'] for art in self.recommender.artworks)
                    return f"I apologize, but we don't have artworks under ₹{filters['max_price']:,}. Our most affordable piece is ₹{min_price:,}. Would you like to see artworks in a different price range?"
                else:
                    return "I couldn't find exact matches for your preferences. Would you like to try different criteria?"
            else:
                return "I couldn't find matches. Could you tell me more about what you're looking for?"

        # Simple message when artworks are found - details shown in cards
        return f"Here are {len(artworks)} stunning artworks that match your preferences! Feel free to explore them below."

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
