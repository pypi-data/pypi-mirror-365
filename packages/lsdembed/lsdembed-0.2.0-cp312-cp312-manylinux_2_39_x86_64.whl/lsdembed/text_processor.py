import re
import math
from collections import defaultdict
from typing import List, Dict

class TextProcessor:
    def __init__(self, token_pattern: str = r'\w+'):
        self.token_pattern = re.compile(token_pattern)
    
    def tokenize(self, text: str) -> List[str]:
        return [token.lower() for token in self.token_pattern.findall(text)]
    
    def chunk_texts(self, texts: List[str], max_chars: int = 300) -> List[str]:
        """
        Splits input texts into chunks of up to max_chars length,
        breaking at paragraph boundaries when possible.
        """
        all_chunks = []
        for text in texts:
            # First split by paragraphs
            paragraphs = re.split(r'\n+', text)
            chunks = []
            current_chunk = ""
            
            for para in paragraphs:
                # If adding the paragraph exceeds max_chars, finalize current chunk
                if len(current_chunk) + len(para) > max_chars:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + para
                    else:
                        current_chunk = para
            
            # Append any remaining text
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def calculate_idf(self, chunks: List[str]) -> Dict[str, float]:
        """Calculates Inverse Document Frequency for semantic mass."""
        doc_freq = defaultdict(int)
        total_docs = len(chunks)
        for chunk in chunks:
            tokens_in_chunk = set(self.tokenize(chunk))
            for token in tokens_in_chunk:
                doc_freq[token] += 1
                
        idf_scores = {
            token: math.log(total_docs / (count + 1))
            for token, count in doc_freq.items()
        }
        print(f"Calculated IDF for {len(idf_scores)} unique tokens.")
        return idf_scores