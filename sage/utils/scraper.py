import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import Dict, Any, List, Optional
import uuid
import datetime
from sage.models.schemas import ProductContext

class WebScraper:
    def __init__(self):
        self.ua = UserAgent()

    def scrape(self, url: str) -> ProductContext:
        html = self._fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        images = self._extract_images(soup)
        # Reviews are often dynamic, this is best-effort for static content
        reviews_text = self._extract_reviews_text(soup) 
        
        # Generate a stable ID if possible, else random
        product_id = str(uuid.uuid5(uuid.NAMESPACE_URL, url))
        
        # Extract technical specs
        specs = self._extract_specs(soup)

        return ProductContext(
            product_id=product_id,
            url=url,
            pdp_html=html, # Store full HTML for chunking later
            images=images,
            source="web_app",
            timestamp=datetime.datetime.now().isoformat(),
            metadata={
                "title": title,
                "description": description,
                "extracted_reviews_length": len(reviews_text),
                "specs": specs
            }
        )

    def _fetch_html(self, url: str) -> str:
        headers = {'User-Agent': self.ua.random}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return "<html><body>Error fetching content</body></html>"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        # OpenGraph
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]

        # Common selectors for Amazon, Flipkart, generic
        selectors = [
            "#productTitle", # Amazon
            "h1.yhB1nd", # Flipkart (class might change)
            "h1",
            "title"
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return "Unknown Product"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        # OpenGraph
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"]

        # Meta description
        meta = soup.find("meta", attrs={"name": "description"})
        if meta:
            return meta.get("content", "")
        
        # Amazon feature bullets
        bullets = soup.select("#feature-bullets li")
        if bullets:
            return "\n".join([b.get_text(strip=True) for b in bullets])
            
        return ""

    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        images = []
        
        # OpenGraph Image
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            images.append(og_img["content"])

        # Find all images, prioritize large ones if possible
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-old-hires")
            if src and src.startswith("http"):
                # Filter out tiny icons/pixels based on heuristics
                if "sprite" in src or "icon" in src or "pixel" in src:
                    continue
                images.append(src)
        return list(set(images))[:10] # Limit to 10 unique images

    def _extract_reviews_text(self, soup: BeautifulSoup) -> str:
        # Attempt to find review containers
        reviews = []
        
        # Common review selectors
        selectors = [
            ".review-text-content", # Amazon
            "[data-hook='review-body']", # Amazon alt
            ".review-text",
            ".comment-content",
            ".user-review"
        ]
        
        for selector in selectors:
            for review in soup.select(selector):
                text = review.get_text(strip=True)
                if len(text) > 20: # Filter out short noise
                    reviews.append(text)
            
        if reviews:
            return "\n\n".join(reviews[:20]) # Limit to top 20 reviews
            
        return ""

    def _extract_specs(self, soup: BeautifulSoup) -> Dict[str, str]:
        specs = {}
        # Look for tables that might be specs
        for table in soup.find_all("table"):
            # Heuristic: tables often have "spec" or "tech" in class or id, or just 2 columns
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all(["th", "td"])
                if len(cols) == 2:
                    key = cols[0].get_text(strip=True)
                    val = cols[1].get_text(strip=True)
                    if key and val and len(key) < 50 and len(val) < 200:
                        specs[key] = val
        return specs
