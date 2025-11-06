"""
Create a curated demo collection with working images and diverse metadata
Uses Met Museum API + manual curation for balanced categories
"""
import json
import requests
from time import sleep

def verify_image(url):
    """Check if image URL works"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def create_curated_collection():
    """Create manually curated collection with verified images"""

    # Curated list of Met Museum artworks with specific IDs that have good images
    # and represent diverse styles, colors, and moods
    curated_artworks = [
        # Portraits - Elegant/Contemplative
        {
            "met_id": 437853,  # Madame X by Sargent
            "style": ["portrait", "classical"],
            "colors": ["black", "white"],
            "mood": ["elegant", "dramatic", "bold"],
            "price": 450000
        },
        {
            "met_id": 436105,  # Portrait of a Woman
            "style": ["portrait", "classical"],
            "colors": ["brown", "gold"],
            "mood": ["elegant", "contemplative"],
            "price": 380000
        },
        {
            "met_id": 438817,  # Young Woman with a Water Pitcher
            "style": ["portrait", "classical"],
            "colors": ["blue", "white", "yellow"],
            "mood": ["serene", "peaceful"],
            "price": 320000
        },
        {
            "met_id": 437397,  # Portrait of a Man (Frans Hals)
            "style": ["portrait", "classical"],
            "colors": ["black", "white"],
            "mood": ["contemplative", "timeless"],
            "price": 410000
        },
        {
            "met_id": 435809,  # Portrait of a Young Woman
            "style": ["portrait", "impressionist"],
            "colors": ["pink", "white"],
            "mood": ["intimate", "elegant"],
            "price": 290000
        },

        # Landscapes - Calming/Serene
        {
            "met_id": 436535,  # The Harvesters (Bruegel)
            "style": ["landscape", "classical"],
            "colors": ["green", "yellow", "brown"],
            "mood": ["serene", "peaceful"],
            "price": 480000
        },
        {
            "met_id": 459051,  # View of Toledo (El Greco)
            "style": ["landscape", "classical"],
            "colors": ["green", "blue", "gray"],
            "mood": ["dramatic", "mysterious"],
            "price": 470000
        },
        {
            "met_id": 438754,  # Wheat Field with Cypresses (Van Gogh)
            "style": ["landscape", "impressionist"],
            "colors": ["yellow", "blue", "green"],
            "mood": ["energetic", "bold"],
            "price": 490000
        },
        {
            "met_id": 436121,  # Landscape with Traveler
            "style": ["landscape", "classical"],
            "colors": ["green", "brown"],
            "mood": ["calming", "peaceful"],
            "price": 260000
        },
        {
            "met_id": 437980,  # The Gulf Stream (Winslow Homer)
            "style": ["landscape", "classical"],
            "colors": ["blue", "green"],
            "mood": ["dramatic", "bold"],
            "price": 350000
        },

        # Abstract/Modern - Bold/Energetic
        {
            "met_id": 488315,  # Composition (Kandinsky-style)
            "style": ["abstract", "contemporary"],
            "colors": ["red", "yellow", "blue"],
            "mood": ["bold", "energetic", "modern"],
            "price": 420000
        },
        {
            "met_id": 488123,  # Abstract composition
            "style": ["abstract", "contemporary"],
            "colors": ["orange", "red", "yellow"],
            "mood": ["energetic", "dramatic"],
            "price": 390000
        },
        {
            "met_id": 489735,  # Modern abstract
            "style": ["abstract", "minimalist"],
            "colors": ["black", "white", "gray"],
            "mood": ["contemplative", "modern"],
            "price": 360000
        },

        # Florals/Still Life - Various moods
        {
            "met_id": 437891,  # Irises (Van Gogh)
            "style": ["impressionist", "fine-art"],
            "colors": ["purple", "blue", "green"],
            "mood": ["serene", "expressive"],
            "price": 440000
        },
        {
            "met_id": 437112,  # Sunflowers
            "style": ["impressionist", "fine-art"],
            "colors": ["yellow", "orange", "brown"],
            "mood": ["joyful", "energetic"],
            "price": 430000
        },

        # Under 2L options
        {
            "met_id": 436535,  # Duplicate OK for demo - will dedupe
            "style": ["classical", "fine-art"],
            "colors": ["brown", "gold"],
            "mood": ["contemplative", "elegant"],
            "price": 180000
        },
        {
            "met_id": 437312,
            "style": ["portrait", "classical"],
            "colors": ["red", "brown"],
            "mood": ["elegant", "dramatic"],
            "price": 250000
        },
        {
            "met_id": 438140,
            "style": ["landscape", "impressionist"],
            "colors": ["blue", "white"],
            "mood": ["peaceful", "serene"],
            "price": 220000
        },
    ]

    artworks = []
    seen_ids = set()

    print("Fetching curated artworks from Met Museum...")
    print("=" * 80)

    for i, config in enumerate(curated_artworks, 1):
        met_id = config['met_id']

        # Skip duplicates
        if met_id in seen_ids:
            continue
        seen_ids.add(met_id)

        print(f"[{i}/{len(curated_artworks)}] Fetching artwork #{met_id}...", end=" ")

        # Fetch artwork details
        try:
            response = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{met_id}", timeout=10)
            if response.status_code != 200:
                print("✗ API Error")
                continue

            data = response.json()
            image_url = data.get('primaryImage')

            if not image_url:
                print("✗ No Image")
                continue

            # Verify image works
            if not verify_image(image_url):
                print("✗ Broken Image")
                continue

            title = data.get('title', 'Untitled')
            artist = data.get('artistDisplayName', '')

            artwork = {
                "id": f"demo_{len(artworks) + 1}",
                "title": title[:60],
                "artist": artist if artist else "",
                "price": config['price'],
                "currency": "INR",
                "style": config['style'],
                "colors": config['colors'],
                "medium": data.get('medium', 'Oil on canvas'),
                "mood": config['mood'],
                "dimensions": data.get('dimensions', 'N/A'),
                "period": data.get('objectDate', 'Unknown'),
                "availability": "available",
                "image_url": image_url,
                "thumbnail_url": data.get('primaryImageSmall', image_url),
                "description": title,
                "department": data.get('department', ''),
                "culture": data.get('culture', '')
            }

            artworks.append(artwork)
            print(f"✓ {title[:40]}")

        except Exception as e:
            print(f"✗ Error: {str(e)[:30]}")

        sleep(0.5)  # Rate limiting

    print("\n" + "=" * 80)
    print(f"Total artworks fetched: {len(artworks)}")

    return artworks

if __name__ == "__main__":
    artworks = create_curated_collection()

    if len(artworks) < 10:
        print("\n⚠️  Warning: Only fetched {len(artworks)} artworks. Needs at least 10.")

    # Save to file
    with open('../data/artworks_demo_new.json', 'w', encoding='utf-8') as f:
        json.dump(artworks, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(artworks)} artworks to artworks_demo_new.json")

    # Print distributions
    styles = {}
    colors = {}
    moods = {}
    for art in artworks:
        for s in art['style']:
            styles[s] = styles.get(s, 0) + 1
        for c in art['colors']:
            colors[c] = colors.get(c, 0) + 1
        for m in art['mood']:
            moods[m] = moods.get(m, 0) + 1

    print("\n📊 Distribution Analysis:")
    print("\nStyles:")
    for style, count in sorted(styles.items(), key=lambda x: x[1], reverse=True):
        print(f"  {style:20} {count}")

    print("\nColors:")
    for color, count in sorted(colors.items(), key=lambda x: x[1], reverse=True):
        print(f"  {color:20} {count}")

    print("\nMoods:")
    for mood, count in sorted(moods.items(), key=lambda x: x[1], reverse=True):
        print(f"  {mood:20} {count}")

    print("\nPrice Range:")
    prices = [art['price'] for art in artworks]
    print(f"  Min: ₹{min(prices):,}")
    print(f"  Max: ₹{max(prices):,}")
    print(f"  Avg: ₹{sum(prices)//len(prices):,}")

    print("\nPrice Distribution:")
    under_2L = len([p for p in prices if p < 200000])
    under_3L = len([p for p in prices if p < 300000])
    under_4L = len([p for p in prices if p < 400000])
    under_5L = len([p for p in prices if p < 500000])
    print(f"  Under ₹2L: {under_2L}")
    print(f"  Under ₹3L: {under_3L}")
    print(f"  Under ₹4L: {under_4L}")
    print(f"  Under ₹5L: {under_5L}")
