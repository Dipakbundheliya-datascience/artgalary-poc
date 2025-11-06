"""
Fetch fresh artworks from Met Museum API with working images
Create a balanced collection across different categories
"""
import json
import requests
from time import sleep

MET_API_BASE = "https://collectionapi.metmuseum.org/public/collection/v1"

def fetch_artwork_details(object_id):
    """Fetch detailed artwork information"""
    try:
        response = requests.get(f"{MET_API_BASE}/objects/{object_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def create_balanced_collection():
    """Create a balanced collection of artworks"""

    # Define search criteria for balanced collection
    searches = [
        # Portraits (5 artworks)
        {"q": "portrait", "hasImages": "true", "departmentId": 11, "count": 5},  # European Paintings

        # Landscapes (5 artworks)
        {"q": "landscape", "hasImages": "true", "departmentId": 11, "count": 5},

        # Abstract/Modern (5 artworks)
        {"q": "abstract", "hasImages": "true", "departmentId": 21, "count": 5},  # Modern Art
    ]

    artworks = []
    artwork_id = 1

    # Price ranges for variety
    price_ranges = [
        (180000, 220000),
        (220000, 280000),
        (280000, 350000),
        (350000, 420000),
        (420000, 500000),
    ]

    print("Fetching fresh artworks from Met Museum API...")
    print("=" * 80)

    for search_config in searches:
        query = search_config['q']
        dept_id = search_config['departmentId']
        target_count = search_config['count']

        print(f"\nSearching for {query} artworks...")

        # Search for artworks
        search_url = f"{MET_API_BASE}/search?hasImages=true&q={query}&departmentId={dept_id}"
        response = requests.get(search_url)

        if response.status_code != 200:
            continue

        data = response.json()
        object_ids = data.get('objectIDs', [])[:50]  # Get first 50 results

        found_count = 0
        for obj_id in object_ids:
            if found_count >= target_count:
                break

            artwork_data = fetch_artwork_details(obj_id)
            if not artwork_data:
                continue

            # Check if it has a valid image
            if not artwork_data.get('primaryImage'):
                continue

            # Verify image URL works
            try:
                img_response = requests.head(artwork_data['primaryImage'], timeout=5)
                if img_response.status_code != 200:
                    continue
            except:
                continue

            # Extract metadata
            title = artwork_data.get('title', 'Untitled')
            artist = artwork_data.get('artistDisplayName', 'Unknown Artist')

            # Assign price from range
            price_range = price_ranges[len(artworks) % len(price_ranges)]
            import random
            price = random.randint(price_range[0], price_range[1])

            # Basic style classification
            classification = artwork_data.get('classification', '').lower()
            object_name = artwork_data.get('objectName', '').lower()

            # Safe year extraction
            try:
                artist_end = int(artwork_data.get('artistEndDate', 0)) if artwork_data.get('artistEndDate') else 0
            except (ValueError, TypeError):
                artist_end = 0

            if 'portrait' in title.lower() or 'portrait' in object_name:
                style = ['portrait', 'classical']
            elif 'landscape' in title.lower() or 'landscape' in object_name:
                style = ['landscape', 'classical']
            elif 'abstract' in classification or artist_end > 1900:
                style = ['abstract', 'contemporary']
            else:
                style = ['classical', 'fine-art']

            artwork = {
                "id": f"demo_{artwork_id}",
                "title": title[:60],  # Limit title length
                "artist": artist if artist != "Unknown Artist" else "",
                "price": price,
                "currency": "INR",
                "style": style,
                "colors": ["multicolor"],  # Will be enriched later
                "medium": artwork_data.get('medium', 'Oil on canvas'),
                "mood": ["contemplative"],  # Will be enriched later
                "dimensions": artwork_data.get('dimensions', 'N/A'),
                "period": artwork_data.get('objectDate', 'Unknown'),
                "availability": "available",
                "image_url": artwork_data['primaryImage'],
                "thumbnail_url": artwork_data.get('primaryImageSmall', artwork_data['primaryImage']),
                "description": artwork_data.get('title', ''),
                "department": artwork_data.get('department', ''),
                "culture": artwork_data.get('culture', '')
            }

            artworks.append(artwork)
            artwork_id += 1
            found_count += 1

            print(f"  ✓ {title[:50]:50} - {artist[:30]}")

            sleep(0.5)  # Rate limiting

    print("\n" + "=" * 80)
    print(f"Total artworks fetched: {len(artworks)}")

    return artworks

if __name__ == "__main__":
    artworks = create_balanced_collection()

    # Save to file
    with open('../data/artworks_demo_new.json', 'w', encoding='utf-8') as f:
        json.dump(artworks, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(artworks)} artworks to artworks_demo_new.json")

    # Print category distribution
    styles = {}
    for art in artworks:
        for s in art['style']:
            styles[s] = styles.get(s, 0) + 1

    print("\nStyle Distribution:")
    for style, count in sorted(styles.items(), key=lambda x: x[1], reverse=True):
        print(f"  {style}: {count}")

    print("\nPrice Range:")
    prices = [art['price'] for art in artworks]
    print(f"  Min: ₹{min(prices):,}")
    print(f"  Max: ₹{max(prices):,}")
    print(f"  Avg: ₹{sum(prices)//len(prices):,}")
