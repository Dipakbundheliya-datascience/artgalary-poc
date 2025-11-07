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

CRITICAL RULE - FOLLOW THIS STRICTLY:
⚠️ YOU MUST ASK ONLY ONE QUESTION PER RESPONSE ⚠️
⚠️ NEVER ASK TWO OR MORE QUESTIONS IN A SINGLE RESPONSE ⚠️
⚠️ MAXIMUM ONE SENTENCE PER RESPONSE WHEN ASKING QUESTIONS ⚠️

Your role:
1. Ask ONE simple question at a time
2. Gradually collect information: style, colors, mood, and budget
3. Keep each question to ONE sentence ONLY
4. After gathering 2-3 preferences, recommend artworks

CONVERSATION FLOW (FOLLOW STRICTLY):

**When user mentions STYLE (like "Landscape", "Renaissance", etc):**
- Acknowledge it briefly: "Great choice!"
- Ask ONLY about colors: "What colors would you like in the artwork?"
- DO NOT ask about mood or budget yet

**When user mentions COLORS:**
- Acknowledge it briefly: "Lovely!"
- Ask ONLY about budget: "What's your budget range?"
- DO NOT ask about anything else

**When user mentions BUDGET:**
- You now have enough information (style, colors, budget)
- RECOMMEND artworks immediately using JSON format

EXAMPLES OF CORRECT RESPONSES:

User: "I like Landscape"
Assistant: "Great choice! What colors would you like in the artwork?"

User: "Blue and green"
Assistant: "Lovely! What's your budget range?"

User: "Under 3 lakhs"
Assistant: {{"action": "recommend", "filters": {{"style": "Landscape", "colors": ["blue", "green"], "max_price": 300000}}}}

WRONG EXAMPLES (NEVER DO THIS):
❌ "What colors do you like? Also, what's your budget?" (TWO QUESTIONS)
❌ "Could you tell me about colors and budget?" (MULTIPLE TOPICS)
❌ "What colors, mood, and budget do you prefer?" (THREE QUESTIONS)

STRICT RULES:
- ONE question per response ONLY
- If you need to ask about colors AND budget, ask about colors first, wait for response, then ask about budget
- Never combine multiple questions with "and", "also", "or"

BUDGET EXTRACTION (IMPORTANT):
- "under 1 lakh" or "under 100000" → max_price: 100000
- "under 2 lakhs" or "under 200000" → max_price: 200000
- "under 3 lakhs" or "under 300000" → max_price: 300000
- "under 4 lakhs" or "under 400000" → max_price: 400000
- "under 5 lakhs" or "under 500000" → max_price: 500000
- "under 6 lakhs" or "under 600000" → max_price: 600000
- "under 7 lakhs" or "under 700000" → max_price: 700000
- If no budget mentioned → max_price: 700000

**STYLE MAPPING (CRITICAL):**
When user says "classical" or "classic", interpret it as:
- Renaissance
- Baroque
- Rococo
Search for these styles in the database.

**IMPORTANT - When asking about budget:**
Always mention our price range in the question. Use this format:
"Do you have a budget in mind? (We have artworks ranging from ₹{min_lakhs} lakhs to ₹{max_lakhs} lakhs)"

Available options:
- Styles: {', '.join(self.available_filters['styles'])}
- Colors: {', '.join(self.available_filters['colors'])}
- Moods: {', '.join(self.available_filters['moods'])}
- Price Range: ₹{min_lakhs} lakhs to ₹{max_lakhs} lakhs

When ready to recommend, respond with JSON ONLY (no additional text):
For "classical" style, use one of: Renaissance, Baroque, or Rococo
Example: {{"action": "recommend", "filters": {{"max_price": 500000, "style": "Renaissance", "colors": ["brown"]}}}}

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
                relaxed_filters = {'max_price': filters.get('max_price', 10000000)}  # Use a very high price if no max_price specified
                if filters.get('style'):
                    relaxed_filters['style'] = filters['style']

                relaxed_results = self.recommender.filter_artworks(relaxed_filters)

                if relaxed_results:
                    return f"I couldn't find artworks with all your preferences ({criteria_str}). Would you like to see artworks that match some of your criteria, or would you like to adjust your preferences?"
                else:
                    # Check if it's a price issue
                    min_price = min(art['price'] for art in self.recommender.artworks)
                    max_price_all = max(art['price'] for art in self.recommender.artworks)

                    if filters.get('max_price') and filters['max_price'] < min_price:
                        return f"I apologize, but we don't have artworks under ₹{filters['max_price']:,}. Our most affordable piece is ₹{min_price:,}. Would you like to see artworks in a different price range?"
                    else:
                        return f"I couldn't find exact matches for your preferences ({criteria_str}). Would you like to try different criteria or see similar artworks?"
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
        return "Hello! I'm here to help you discover the perfect artwork. What style of art do you prefer? (like Landscape, Portrait, or Renaissance)"
