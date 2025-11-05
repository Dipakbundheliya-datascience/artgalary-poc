import requests
import json
import time
import random

# Met Museum API endpoint
BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

def fetch_artwork_details(object_id):
    """Fetch detailed information for a specific artwork"""
    try:
        response = requests.get(f"{BASE_URL}/objects/{object_id}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching object {object_id}: {e}")
    return None

def categorize_style(artwork):
    """Categorize artwork style based on metadata"""
    classification = artwork.get('classification', '').lower()
    culture = artwork.get('culture', '').lower()
    period = artwork.get('period', '').lower()
    title = artwork.get('title', '').lower()

    styles = []

    if any(word in classification or word in title for word in ['abstract', 'modern']):
        styles.append('abstract')
    if any(word in period or word in culture for word in ['contemporary', 'modern', '20th', '21st']):
        styles.append('contemporary')
    if any(word in culture or word in period for word in ['impressionist', 'post-impressionist']):
        styles.append('impressionist')
    if any(word in culture or word in period for word in ['renaissance', 'baroque', 'classical']):
        styles.append('classical')
    if 'landscape' in classification or 'landscape' in title:
        styles.append('landscape')
    if 'portrait' in classification or 'portrait' in title:
        styles.append('portrait')

    return styles if styles else ['fine-art']

def extract_colors(artwork):
    """Extract dominant colors from artwork metadata"""
    title = artwork.get('title', '').lower()
    medium = artwork.get('medium', '').lower()

    color_map = {
        'red': ['red', 'crimson', 'scarlet'],
        'blue': ['blue', 'azure', 'cobalt'],
        'yellow': ['yellow', 'gold', 'golden'],
        'green': ['green', 'emerald'],
        'black': ['black', 'dark'],
        'white': ['white', 'ivory'],
        'brown': ['brown', 'sepia', 'umber'],
        'orange': ['orange'],
        'purple': ['purple', 'violet'],
        'pink': ['pink', 'rose']
    }

    colors = []
    for color, keywords in color_map.items():
        if any(keyword in title or keyword in medium for keyword in keywords):
            colors.append(color)

    return colors if colors else ['multicolor']

def assign_mood(styles, colors):
    """Assign mood based on style and colors"""
    moods = []

    if 'abstract' in styles or 'contemporary' in styles:
        moods.extend(['bold', 'modern'])
    if 'classical' in styles or 'renaissance' in styles:
        moods.extend(['elegant', 'timeless'])
    if 'landscape' in styles:
        moods.extend(['serene', 'peaceful'])
    if 'portrait' in styles:
        moods.extend(['intimate', 'expressive'])

    if 'red' in colors or 'orange' in colors:
        moods.append('energetic')
    if 'blue' in colors or 'green' in colors:
        moods.append('calming')
    if 'black' in colors:
        moods.append('dramatic')

    return list(set(moods)) if moods else ['contemplative']

def transform_to_schema(artwork):
    """Transform Met Museum data to our schema"""
    if not artwork.get('primaryImage'):
        return None

    styles = categorize_style(artwork)
    colors = extract_colors(artwork)
    moods = assign_mood(styles, colors)

    # Generate realistic Indian art prices (50K to 5L INR)
    base_price = random.randint(50000, 500000)
    price = round(base_price / 10000) * 10000

    return {
        "id": str(artwork['objectID']),
        "title": artwork.get('title', 'Untitled'),
        "artist": artwork.get('artistDisplayName', 'Unknown Artist'),
        "price": price,
        "currency": "INR",
        "style": styles,
        "colors": colors,
        "medium": artwork.get('medium', 'Mixed media'),
        "mood": moods,
        "dimensions": artwork.get('dimensions', 'Not specified'),
        "period": artwork.get('objectDate', 'Unknown'),
        "availability": "available",
        "image_url": artwork.get('primaryImage'),
        "thumbnail_url": artwork.get('primaryImageSmall'),
        "description": f"{artwork.get('culture', 'Art')} artwork from {artwork.get('objectDate', 'historical period')}. {artwork.get('creditLine', '')}",
        "department": artwork.get('department', 'Fine Arts'),
        "culture": artwork.get('culture', 'Various')
    }

def fetch_diverse_artworks(target_count=40):
    """Fetch diverse artworks from different departments"""

    # Search queries for diverse artwork types
    search_queries = [
        'painting',
        'abstract',
        'landscape',
        'portrait',
        'modern',
        'contemporary',
        'floral',
        'still life'
    ]

    artworks = []
    seen_ids = set()

    for query in search_queries:
        if len(artworks) >= target_count:
            break

        print(f"Searching for: {query}")
        try:
            # Search for artworks
            response = requests.get(f"{BASE_URL}/search", params={
                'q': query,
                'hasImages': 'true'
            })

            if response.status_code == 200:
                data = response.json()
                object_ids = data.get('objectIDs', [])

                if object_ids:
                    # Sample random artworks from results
                    sample_size = min(10, len(object_ids))
                    sampled_ids = random.sample(object_ids, sample_size)

                    for obj_id in sampled_ids:
                        if len(artworks) >= target_count:
                            break

                        if obj_id in seen_ids:
                            continue

                        print(f"Fetching artwork {obj_id}...")
                        artwork_data = fetch_artwork_details(obj_id)

                        if artwork_data:
                            transformed = transform_to_schema(artwork_data)
                            if transformed:
                                artworks.append(transformed)
                                seen_ids.add(obj_id)
                                print(f"✓ Added: {transformed['title']}")

                        time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"Error searching for {query}: {e}")

    return artworks

if __name__ == "__main__":
    print("Fetching artworks from The Met Museum...")
    print("=" * 50)

    artworks = fetch_diverse_artworks(40)

    print(f"\n✓ Successfully fetched {len(artworks)} artworks")

    # Save to JSON
    output_path = "../data/artworks.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(artworks, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved to {output_path}")

    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    all_styles = set()
    all_colors = set()
    all_moods = set()
    price_range = [artwork['price'] for artwork in artworks]

    for artwork in artworks:
        all_styles.update(artwork['style'])
        all_colors.update(artwork['colors'])
        all_moods.update(artwork['mood'])

    print(f"Total artworks: {len(artworks)}")
    print(f"Styles: {', '.join(sorted(all_styles))}")
    print(f"Colors: {', '.join(sorted(all_colors))}")
    print(f"Moods: {', '.join(sorted(all_moods))}")
    print(f"Price range: ₹{min(price_range):,} - ₹{max(price_range):,}")
