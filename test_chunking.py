from sage.utils.chunking import Chunker

def test_chunking():
    chunker = Chunker()
    
    print("--- Testing Chunker ---")
    
    # 1. PDP
    pdp_text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
    chunks = chunker.chunk(pdp_text, "pdp")
    print(f"PDP Chunks ({len(chunks)}): {chunks}")
    
    # 2. YouTube
    transcript = [
        {"text": "Hello world.", "start": 0, "duration": 10},
        {"text": "This is a test.", "start": 10, "duration": 10},
        {"text": "Still testing.", "start": 20, "duration": 15} # Total 35s
    ]
    chunks = chunker.chunk(transcript, "youtube")
    print(f"YouTube Chunks ({len(chunks)}): {chunks}")
    
    # 3. Reddit
    thread = {
        "title": "My Review",
        "selftext": "It is good.",
        "comments": ["I agree.", "I disagree."]
    }
    chunks = chunker.chunk(thread, "reddit")
    print(f"Reddit Chunks ({len(chunks)}): {chunks}")

if __name__ == "__main__":
    test_chunking()
