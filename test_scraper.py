from sage.utils.scraper import WebScraper

def test_scraper():
    scraper = WebScraper()
    
    # Test with a real URL (using a generic one that is likely to exist, or just example.com)
    # Note: Amazon/Flipkart might block requests without advanced headers/proxies.
    # We'll try a simple page first.
    url = "https://www.example.com" 
    print(f"Scraping {url}...")
    
    context = scraper.scrape(url)
    
    print(f"Product ID: {context.product_id}")
    print(f"Title: {context.metadata.get('title')}")
    print(f"HTML Length: {len(context.pdp_html)}")
    print(f"Images Found: {len(context.images)}")
    
    # If you want to test with a real product URL manually, uncomment below:
    # url = "https://www.amazon.com/dp/B08N5WRWNW" # Example
    # context = scraper.scrape(url)
    # print(f"Amazon Title: {context.metadata.get('title')}")

if __name__ == "__main__":
    test_scraper()
