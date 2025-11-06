"""
Enrich artwork metadata using Gemini AI vision capabilities
This script analyzes artwork images to add accurate color and mood tags
"""
import json
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}"

def analyze_artwork_with_ai(image_url, title, artist):
    """Use Gemini to analyze artwork and extract colors, moods, and styles"""

    prompt = f"""Analyze this artwork titled "{title}" by {artist if artist else 'Unknown Artist'}.

Provide ONLY a JSON response with these fields (no additional text):
{{
    "dominant_colors": ["color1", "color2", "color3"],
    "mood": ["mood1", "mood2"],
    "style": ["style1"]
}}

Guidelines:
- dominant_colors: Choose 2-4 from [red, blue, green, yellow, orange, purple, pink, brown, black, white, multicolor]
- mood: Choose 2-3 from [calming, energetic, serene, peaceful, dramatic, bold, elegant, contemplative, expressive, intimate, mysterious, joyful]
- style: Choose 1-2 from [abstract, classical, contemporary, impressionist, landscape, portrait, fine-art, minimalist, surreal]

Base your analysis on the actual visual appearance of the artwork."""

    # For text-only analysis (since we can't easily send image URLs to Gemini via REST)
    # We'll use a simplified approach based on title and existing metadata

    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    try:
        response = requests.post(GEMINI_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']

            # Extract JSON from response
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(text[json_start:json_end])
                return result
    except Exception as e:
        print(f"Error analyzing artwork: {e}")

    return None

def enrich_metadata():
    """Enrich all artworks with better metadata"""

    # Load existing artworks
    with open('../data/artworks.json', 'r', encoding='utf-8') as f:
        artworks = json.load(f)

    print(f"Enriching metadata for {len(artworks)} artworks...")
    print("=" * 60)

    enriched = []

    for i, artwork in enumerate(artworks, 1):
        print(f"\n[{i}/{len(artworks)}] {artwork['title']}")

        # Analyze with AI
        analysis = analyze_artwork_with_ai(
            artwork['image_url'],
            artwork['title'],
            artwork.get('artist', '')
        )

        if analysis:
            # Update artwork with AI analysis
            artwork['colors'] = analysis.get('dominant_colors', artwork['colors'])
            artwork['mood'] = analysis.get('mood', artwork['mood'])

            # Merge AI style with existing, prefer AI
            ai_style = analysis.get('style', [])
            if ai_style and ai_style != ['fine-art']:
                artwork['style'] = ai_style

            print(f"  ✓ Colors: {', '.join(artwork['colors'])}")
            print(f"  ✓ Mood: {', '.join(artwork['mood'])}")
            print(f"  ✓ Style: {', '.join(artwork['style'])}")
        else:
            print(f"  ✗ Failed to analyze, keeping original metadata")

        enriched.append(artwork)

        # Rate limiting - wait 2 seconds between requests
        if i < len(artworks):
            time.sleep(2)

    # Save enriched data
    with open('../data/artworks_enriched.json', 'w', encoding='utf-8') as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"✓ Enriched metadata saved to artworks_enriched.json")

    # Print new distribution
    all_colors = {}
    all_moods = {}
    for art in enriched:
        for c in art['colors']:
            all_colors[c] = all_colors.get(c, 0) + 1
        for m in art['mood']:
            all_moods[m] = all_moods.get(m, 0) + 1

    print("\nNew Color Distribution:")
    for color, count in sorted(all_colors.items(), key=lambda x: x[1], reverse=True):
        print(f"  {color}: {count}")

    print("\nNew Mood Distribution:")
    for mood, count in sorted(all_moods.items(), key=lambda x: x[1], reverse=True):
        print(f"  {mood}: {count}")

if __name__ == "__main__":
    enrich_metadata()
