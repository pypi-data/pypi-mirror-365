from .similarity import combined_similarity
from .sentiment import sentimental_score
from .utils import count_overlapping_words

def compute_empathy_score(context, response, reference, model, tokenizer):
    relevance = combined_similarity(response, reference, model, tokenizer)
    sentiment = sentimental_score(context, response)
    overlap_count = count_overlapping_words(context, response)
    overlap = overlap_count / len(response.split())
    
    return {
        "relevance_score": relevance,
        "sentiment_score": sentiment,
        "overlap_score": overlap,
        "empathy_score": (relevance + sentiment + overlap) / 3
    }
