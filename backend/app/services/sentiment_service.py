"""
Simple keyword-based sentiment analysis. Phase 4 feature.
No ML model needed — fast enough for real-time chat scoring.
"""

_NEGATIVE = {
    "frustrated", "frustrating", "angry", "annoyed", "terrible", "horrible", "awful",
    "useless", "broken", "stupid", "hate", "worst", "pathetic", "garbage", "ridiculous",
    "unacceptable", "disappointed", "failing", "failed", "not working", "doesnt work",
    "doesn't work", "wrong", "incorrect", "impossible", "waste", "bad", "poor",
    "unhelpful", "confusing", "confused", "lost", "upset", "absurd", "trash",
    "nonsense", "clueless", "rubbish", "deplorable", "disgusting", "angry", "furious",
}

_POSITIVE = {
    "great", "excellent", "perfect", "amazing", "wonderful", "helpful", "thanks",
    "thank you", "awesome", "love", "fantastic", "good", "nice", "clear", "easy",
    "worked", "works", "found", "solved", "appreciated", "brilliant", "superb",
    "outstanding", "impressive", "happy", "glad", "pleased", "satisfied", "correct",
}


def analyze_sentiment(text: str) -> str:
    """Returns 'positive', 'neutral', or 'negative' based on keyword scoring."""
    lower = text.lower()
    neg = sum(1 for w in _NEGATIVE if w in lower)
    pos = sum(1 for w in _POSITIVE if w in lower)
    if neg > pos:
        return "negative"
    if pos > neg:
        return "positive"
    return "neutral"
