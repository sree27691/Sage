from typing import List, Dict, Any, Union
import re

class Chunker:
    def chunk(self, data: Any, source_type: str) -> List[str]:
        if source_type == "pdp":
            return self._chunk_pdp_html(data)
        elif source_type == "youtube":
            return self._chunk_youtube_transcript(data)
        elif source_type == "reddit":
            return self._chunk_reddit_thread(data)
        elif source_type == "reviews":
            return self._chunk_reviews(data)
        elif source_type == "vlm_image":
            return self._chunk_vlm_image(data)
        else:
            return [str(data)]

    def _chunk_pdp_html(self, html: str) -> List[str]:
        """
        Extract text from HTML and chunk it into manageable segments.
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()
                
            # Get text
            text = soup.get_text(separator='\n')
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text_clean = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Now split into chunks of approx 1000 characters (approx 250 tokens)
            # This is a simple character-based chunker
            chunk_size = 2000
            overlap = 200
            
            final_chunks = []
            for i in range(0, len(text_clean), chunk_size - overlap):
                final_chunks.append(text_clean[i:i + chunk_size])
                
            return final_chunks
            
        except ImportError:
            # Fallback if bs4 not available (though it should be)
            return [html[i:i+2000] for i in range(0, len(html), 1800)]
        except Exception as e:
            print(f"Error chunking HTML: {e}")
            # Fallback to simple slicing
            return [html[i:i+2000] for i in range(0, len(html), 1800)]

    def _chunk_youtube_transcript(self, transcript: List[Dict[str, Any]]) -> List[str]:
        """
        Timestamp-based chunking (~30–45s segments).
        Input expected: List of {'text': str, 'start': float, 'duration': float}
        """
        chunks = []
        current_chunk = []
        current_duration = 0
        
        for segment in transcript:
            current_chunk.append(segment['text'])
            current_duration += segment.get('duration', 0)
            
            if current_duration >= 30: # Chunk every ~30 seconds
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_duration = 0
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

    def _chunk_reddit_thread(self, thread: Dict[str, Any]) -> List[str]:
        """
        Post = 1 chunk; Comments = 1–2 chunks.
        Input expected: {'title': str, 'selftext': str, 'comments': [str]}
        """
        chunks = []
        # Post chunk
        post_text = f"Title: {thread.get('title', '')}\nBody: {thread.get('selftext', '')}"
        chunks.append(post_text)
        
        # Comment chunks
        for comment in thread.get('comments', []):
            # If comment is very long, split it (simple heuristic)
            if len(comment) > 1000:
                mid = len(comment) // 2
                chunks.append(comment[:mid])
                chunks.append(comment[mid:])
            else:
                chunks.append(comment)
                
        return chunks

    def _chunk_reviews(self, reviews: Union[str, List[str]]) -> List[str]:
        """
        1 chunk per review.
        """
        if isinstance(reviews, str):
            return [reviews]
        return reviews

    def _chunk_vlm_image(self, image_data: Dict[str, Any]) -> List[str]:
        """
        1 chunk per image + structured JSON.
        Input expected: VLM output dict
        """
        # Convert structured VLM output to a text representation for embedding
        text = f"Specs: {image_data.get('specs_detected', [])}\nCaptions: {image_data.get('captions', [])}"
        return [text]
