import json
from typing import List, Dict, Any

class ArtworkRecommender:
    def __init__(self, artworks_path: str = "../data/artworks.json"):
        with open(artworks_path, 'r', encoding='utf-8') as f:
            self.artworks = json.load(f)

    def filter_artworks(self, filters: Dict[str, Any]) -> List[Dict]:
        """Filter artworks based on user preferences"""
        results = self.artworks.copy()

        # Filter by style
        if filters.get('style'):
            style = filters['style'].lower()
            results = [
                art for art in results
                if any(style in s.lower() for s in art['style'])
            ]

        # Filter by colors
        if filters.get('colors'):
            user_colors = [c.lower() for c in filters['colors']]
            results = [
                art for art in results
                if any(uc in [ac.lower() for ac in art['colors']] for uc in user_colors)
            ]

        # Filter by mood
        if filters.get('mood'):
            mood = filters['mood'].lower()
            results = [
                art for art in results
                if any(mood in m.lower() for m in art['mood'])
            ]

        # Filter by price range
        if filters.get('max_price'):
            max_price = filters['max_price']
            results = [art for art in results if art['price'] <= max_price]

        if filters.get('min_price'):
            min_price = filters['min_price']
            results = [art for art in results if art['price'] >= min_price]

        return results

    def score_artwork(self, artwork: Dict, filters: Dict[str, Any]) -> float:
        """Score artwork based on how well it matches filters"""
        score = 0.0

        # Style match (weight: 3)
        if filters.get('style'):
            style = filters['style'].lower()
            if any(style in s.lower() for s in artwork['style']):
                score += 3.0

        # Color match (weight: 2)
        if filters.get('colors'):
            user_colors = [c.lower() for c in filters['colors']]
            matches = sum(
                1 for uc in user_colors
                if uc in [ac.lower() for ac in artwork['colors']]
            )
            score += matches * 2.0

        # Mood match (weight: 1.5)
        if filters.get('mood'):
            mood = filters['mood'].lower()
            if any(mood in m.lower() for m in artwork['mood']):
                score += 1.5

        # Price preference (weight: 1)
        if filters.get('max_price'):
            max_price = filters['max_price']
            if artwork['price'] <= max_price * 0.8:
                score += 1.0

        return score

    def recommend(self, filters: Dict[str, Any], limit: int = 5) -> List[Dict]:
        """Get top N recommended artworks"""
        # First filter
        filtered = self.filter_artworks(filters)

        # If no matches, return popular items
        if not filtered:
            filtered = sorted(self.artworks, key=lambda x: x['price'], reverse=True)[:limit]
            return filtered

        # Score and sort
        scored = [(art, self.score_artwork(art, filters)) for art in filtered]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Return top N
        return [art for art, score in scored[:limit]]

    def get_available_filters(self) -> Dict[str, List[str]]:
        """Get all available filter options"""
        styles = set()
        colors = set()
        moods = set()

        for art in self.artworks:
            styles.update(art['style'])
            colors.update(art['colors'])
            moods.update(art['mood'])

        return {
            'styles': sorted(list(styles)),
            'colors': sorted(list(colors)),
            'moods': sorted(list(moods))
        }
