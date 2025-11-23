from sage.utils.external_search import ExternalSearch
from sage.utils.scraper import WebScraper
import json

def test_search():
    print("Testing External Search...")
    es = ExternalSearch()
    
    print("Reddit Search:")
    reddit = es.search_reddit("Sony WH-1000XM5")
    print(json.dumps(reddit[:1], indent=2))
    
    print("\nYouTube Search:")
    youtube = es.search_youtube("Sony WH-1000XM5 Review")
    print(json.dumps(youtube[:1], indent=2))

def test_scraper():
    print("\nTesting Scraper (Mock URL)...")
    scraper = WebScraper()
    # We can't easily test a real URL without internet access guaranteed or a specific target.
    # But we can check if the methods exist.
    print("Scraper initialized.")
    if hasattr(scraper, '_extract_specs'):
        print("Specs extraction method found.")
    else:
        print("ERROR: Specs extraction method MISSING.")

if __name__ == "__main__":
    test_search()
    test_scraper()
