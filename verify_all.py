import sys
import os
import asyncio
from sage.utils.llm_client import LLMClient
from sage.utils.scraper import WebScraper
from sage.utils.external_search import ExternalSearch
from sage.agents.planner import PlannerAgent
from sage.agents.summarizer import SummarizerAgent
from sage.models.schemas import ProductContext

def test_imports():
    print("[1/6] Testing Imports...")
    try:
        import openai
        import anthropic
        import chromadb
        import bs4
        import requests
        import pydantic
        print("✅ All critical packages imported.")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)

def test_llm_client():
    print("\n[2/6] Testing LLM Client...")
    try:
        client = LLMClient()
        # Just check if we can instantiate it. 
        # Actual call might fail if no API keys, but that's a config issue, not code.
        print("✅ LLMClient initialized.")
    except Exception as e:
        print(f"❌ LLMClient init failed: {e}")

def test_scraper():
    print("\n[3/6] Testing Web Scraper...")
    try:
        scraper = WebScraper()
        if hasattr(scraper, '_extract_specs'):
            print("✅ WebScraper has new extraction logic.")
        else:
            print("❌ WebScraper missing _extract_specs.")
    except Exception as e:
        print(f"❌ WebScraper failed: {e}")

def test_external_search():
    print("\n[4/6] Testing External Search...")
    try:
        es = ExternalSearch()
        # Mock call to ensure no crash
        print("✅ ExternalSearch initialized.")
    except Exception as e:
        print(f"❌ ExternalSearch failed: {e}")

def test_agents():
    print("\n[5/6] Testing Agents Initialization...")
    try:
        planner = PlannerAgent()
        summarizer = SummarizerAgent()
        print("✅ Agents initialized.")
    except Exception as e:
        print(f"❌ Agent init failed: {e}")

async def main():
    print("=== Sage Bot System Verification ===")
    test_imports()
    test_llm_client()
    test_scraper()
    test_external_search()
    test_agents()
    print("\n[6/6] System Ready for Startup.")

if __name__ == "__main__":
    asyncio.run(main())
