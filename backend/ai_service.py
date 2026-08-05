import re
import math
from typing import List, Dict, Any

SAMPLE_NOTES = [
    {"id": 1, "text": "Binary search requires a sorted array and repeatedly halves the search range using a midpoint comparison."},
    {"id": 2, "text": "Insertion sort builds a sorted list one element at a time by shifting larger elements to the right."},
    {"id": 3, "text": "FastAPI uses Pydantic models to validate request bodies and automatically generates Swagger documentation."},
    {"id": 4, "text": "SQL joins combine rows from two tables using a matching column, such as inner join, left join, and full join."},
    {"id": 5, "text": "Prompt engineering structures a task, context, constraints, and desired output format to guide an LLM's response."},
]

VOCABULARY = [
    "sort", "search", "binary", "insertion",
    "sql", "join", "fastapi", "pydantic",
    "prompt", "llm", "database", "validate"
]


def summarize_notes(raw_text: str) -> Dict[str, Any]:
    """
    Summarizes raw study notes into a fixed JSON shape containing:
    - topic: derived from first line / title or most frequent word (fallback to 'untitled' for empty)
    - key_points: up to 3 non-empty sentences stripped of whitespace ([] for empty)
    - difficulty: 'easy' (<40 words), 'medium' (40-100 words), 'hard' (>100 words)
    """
    stripped = raw_text.strip() if raw_text else ""
    
    if not stripped:
        return {
            "topic": "untitled",
            "key_points": [],
            "difficulty": "easy"
        }
    
    # Calculate word count for difficulty
    words = re.findall(r'\w+', stripped)
    word_count = len(words)
    
    if word_count < 40:
        difficulty = "easy"
    elif word_count <= 100:
        difficulty = "medium"
    else:
        difficulty = "hard"
        
    # Key points: split by sentence terminators . ! ?
    raw_sentences = re.split(r'[.!?]+', stripped)
    key_points = [s.strip() for s in raw_sentences if s.strip()][:3]
    
    # Topic derivation: title-like first line or most frequent word
    first_line = stripped.splitlines()[0].strip()
    if len(first_line) > 0 and len(first_line) <= 50:
        topic = first_line
    else:
        # Fallback to most frequent non-trivial word (length > 3)
        word_freq = {}
        for w in words:
            w_lower = w.lower()
            if len(w_lower) > 3:
                word_freq[w_lower] = word_freq.get(w_lower, 0) + 1
        if word_freq:
            topic = max(word_freq, key=word_freq.get).capitalize()
        else:
            topic = first_line[:30] + "..." if len(first_line) > 30 else first_line

    return {
        "topic": topic,
        "key_points": key_points,
        "difficulty": difficulty
    }


def mock_embed(text: str) -> List[float]:
    """
    Deterministically turns any input string into a fixed 12-length numeric vector over VOCABULARY.
    Tokenization: lowercase, split on non-alphanumeric characters. Exact whole-token match count.
    """
    if not text:
        return [0.0] * len(VOCABULARY)
        
    tokens = re.findall(r'\w+', text.lower())
    token_counts = {}
    for token in tokens:
        token_counts[token] = token_counts.get(token, 0) + 1
        
    vector = [float(token_counts.get(word, 0)) for word in VOCABULARY]
    return vector


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Computes cosine similarity between vec_a and vec_b from first principles.
    Returns 0.0 directly if either vector's L2 norm is 0 to avoid ZeroDivisionError.
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
        
    similarity = dot_product / (norm_a * norm_b)
    return round(similarity, 4)


def search_notes(query: str) -> List[Dict[str, Any]]:
    """
    Embeds each sample note and query using mock_embed, computes cosine_similarity,
    and returns ranked notes with scores descending.
    """
    query_vec = mock_embed(query)
    results = []
    
    for note in SAMPLE_NOTES:
        note_vec = mock_embed(note["text"])
        score = cosine_similarity(query_vec, note_vec)
        results.append({
            "id": note["id"],
            "text": note["text"],
            "score": score
        })
        
    # Sort results by score descending. For tie scores (e.g. 0.0), maintain original ID order
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
