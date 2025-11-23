import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import List, Dict, Any
import urllib.parse

class ExternalSearch:
    def __init__(self):
        self.ua = UserAgent()

    def search_reddit(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Best-effort Reddit search using their public JSON endpoint.
        Note: This is rate-limited and may be blocked without API auth.
        """
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.reddit.com/search.json?q={encoded_query}&limit={limit}"
        headers = {'User-Agent': self.ua.random}
        
        results = []
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                children = data.get("data", {}).get("children", [])
                for child in children:
                    post = child.get("data", {})
                    results.append({
                        "title": post.get("title"),
                        "text": post.get("selftext", "")[:500], # Truncate
                        "url": f"https://www.reddit.com{post.get('permalink')}",
                        "score": post.get("score"),
                        "comments": post.get("num_comments"),
                        "source": "reddit"
                    })
            else:
                print(f"Reddit search failed: {response.status_code}")
        except Exception as e:
            print(f"Reddit search error: {e}")
            
        # Fallback if empty (so pipeline has something to show for "integration")
        if not results:
            results.append({
                "title": "Reddit Search Unavailable",
                "text": "Could not fetch live Reddit threads without API credentials. Please configure Reddit API.",
                "url": "https://www.reddit.com",
                "source": "reddit"
            })
            
        return results

    def search_youtube(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Best-effort YouTube search scraping.
        Very fragile, depends on DOM structure.
        """
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        headers = {'User-Agent': self.ua.random}
        
        results = []
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # YouTube is heavy JS, this might not get much from raw HTML.
                # We look for script data or simple titles if rendered.
                # Actually, raw HTML often contains "title":{"runs":[{"text":"..."}]} in scripts.
                # A simpler approach for demo: just return a placeholder if we can't easily parse.
                
                # Attempt to find video titles in scripts (simple regex might be better but let's stick to basic)
                import re
                video_ids = re.findall(r"\"videoId\":\"([a-zA-Z0-9_-]{11})\"", response.text)
                titles = re.findall(r"\"title\":\{\"runs\":\[\{\"text\":\"([^\"]+)\"\}\]", response.text)
                
                for i in range(min(len(video_ids), len(titles), limit)):
                    results.append({
                        "title": titles[i],
                        "text": f"Video result for {query}",
                        "url": f"https://www.youtube.com/watch?v={video_ids[i]}",
                        "source": "youtube"
                    })
        except Exception as e:
            print(f"YouTube search error: {e}")

        if not results:
             results.append({
                "title": "YouTube Search Unavailable",
                "text": "Could not fetch live YouTube results without API credentials.",
                "url": "https://www.youtube.com",
                "source": "youtube"
            })
            
        return results
