"""Online image search functionality using various APIs"""

import requests
import logging
from config import Config

logger = logging.getLogger(__name__)


class OnlineImageSearch:
    """Handle online image search from multiple providers"""

    def __init__(self):
        self.unsplash_key = Config.UNSPLASH_ACCESS_KEY
        self.pexels_key = Config.PEXELS_API_KEY
        self.pixabay_key = Config.PIXABAY_API_KEY

    def search_unsplash(self, query, limit=20):
        """
        Search images on Unsplash
        Free tier: 50 requests/hour
        """
        if not self.unsplash_key:
            logger.warning("Unsplash API key not configured")
            return []

        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
            params = {
                "query": query,
                "per_page": min(limit, 30),  # Max 30 per request
                "orientation": "landscape"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get('results', []):
                results.append({
                    'id': item['id'],
                    'source': 'unsplash',
                    'url': item['urls']['regular'],
                    'thumb_url': item['urls']['small'],
                    'download_url': item['links']['download'],
                    'author': item['user']['name'],
                    'author_url': item['user']['links']['html'],
                    'description': item.get('description') or item.get('alt_description') or query,
                    'width': item['width'],
                    'height': item['height'],
                    'likes': item['likes']
                })

            logger.info(f"Unsplash search for '{query}': {len(results)} results")
            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Unsplash search error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Unsplash search: {e}")
            return []

    def search_pexels(self, query, limit=20):
        """
        Search images on Pexels
        Free tier: 200 requests/hour
        """
        if not self.pexels_key:
            logger.warning("Pexels API key not configured")
            return []

        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_key}
            params = {
                "query": query,
                "per_page": min(limit, 80),  # Max 80 per request
                "orientation": "landscape"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get('photos', []):
                results.append({
                    'id': item['id'],
                    'source': 'pexels',
                    'url': item['src']['large'],
                    'thumb_url': item['src']['medium'],
                    'download_url': item['src']['original'],
                    'author': item['photographer'],
                    'author_url': item['photographer_url'],
                    'description': item.get('alt') or query,
                    'width': item['width'],
                    'height': item['height']
                })

            logger.info(f"Pexels search for '{query}': {len(results)} results")
            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Pexels search error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Pexels search: {e}")
            return []

    def search_pixabay(self, query, limit=20):
        """
        Search images on Pixabay
        Free tier: 100 requests/minute
        """
        if not self.pixabay_key:
            logger.warning("Pixabay API key not configured")
            return []

        try:
            url = "https://pixabay.com/api/"
            params = {
                "key": self.pixabay_key,
                "q": query,
                "image_type": "photo",
                "per_page": min(limit, 200),  # Max 200 per request
                "safesearch": "true"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get('hits', []):
                results.append({
                    'id': item['id'],
                    'source': 'pixabay',
                    'url': item['largeImageURL'],
                    'thumb_url': item['webformatURL'],
                    'download_url': item['largeImageURL'],
                    'author': item['user'],
                    'author_url': f"https://pixabay.com/users/{item['user']}-{item['user_id']}/",
                    'description': item.get('tags') or query,
                    'width': item['imageWidth'],
                    'height': item['imageHeight'],
                    'views': item['views'],
                    'downloads': item['downloads']
                })

            logger.info(f"Pixabay search for '{query}': {len(results)} results")
            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Pixabay search error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Pixabay search: {e}")
            return []

    def search_all_providers(self, query, limit=20):
        """
        Search across all configured providers
        """
        all_results = []

        # Try each provider
        if self.unsplash_key:
            all_results.extend(self.search_unsplash(query, limit // 3))

        if self.pexels_key:
            all_results.extend(self.search_pexels(query, limit // 3))

        if self.pixabay_key:
            all_results.extend(self.search_pixabay(query, limit // 3))

        # If no API keys configured, return empty with warning
        if not all_results:
            logger.warning("No online search providers configured. Please add API keys.")

        return all_results[:limit]

    def search(self, query, provider='auto', limit=20):
        """
        Main search method

        Args:
            query: Search query string
            provider: 'unsplash', 'pexels', 'pixabay', 'all', or 'auto'
            limit: Maximum number of results

        Returns:
            List of image results
        """
        if not query:
            return []

        # Auto-detect which provider to use
        if provider == 'auto':
            if self.unsplash_key:
                provider = 'unsplash'
            elif self.pexels_key:
                provider = 'pexels'
            elif self.pixabay_key:
                provider = 'pixabay'
            else:
                provider = 'all'

        # Route to appropriate provider
        if provider == 'unsplash':
            return self.search_unsplash(query, limit)
        elif provider == 'pexels':
            return self.search_pexels(query, limit)
        elif provider == 'pixabay':
            return self.search_pixabay(query, limit)
        elif provider == 'all':
            return self.search_all_providers(query, limit)
        else:
            logger.error(f"Unknown provider: {provider}")
            return []


# Singleton instance
_search_instance = None


def get_online_search():
    """Get or create the online search instance"""
    global _search_instance
    if _search_instance is None:
        _search_instance = OnlineImageSearch()
    return _search_instance


def search_online_images(query, provider='auto', limit=20):
    """
    Convenience function for online image search

    Args:
        query: Search query string
        provider: 'unsplash', 'pexels', 'pixabay', 'all', or 'auto'
        limit: Maximum number of results

    Returns:
        List of image results with metadata
    """
    searcher = get_online_search()
    return searcher.search(query, provider, limit)


def is_online_search_available():
    """Check if any online search provider is configured"""
    return bool(
        Config.UNSPLASH_ACCESS_KEY or
        Config.PEXELS_API_KEY or
        Config.PIXABAY_API_KEY
    )
