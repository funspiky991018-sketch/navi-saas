import re

# Clean and normalize text
def clean_text(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
    words = text.split()

    # Common stopwords to ignore
    stopwords = {
        "the", "and", "or", "with", "a", "an", "to", "for",
        "in", "on", "of", "at", "by", "is", "are", "was",
        "i", "you", "he", "she", "it", "we", "they", "my",
        "your", "their", "our", "has", "have", "had", "as",
        "that", "this", "from", "be", "but", "if", "not", "so",
        "looking", "skilled"  # optional: remove generic words
    }

    return {word for word in words if word not in stopwords}


# Generate improvement suggestions
def generate_suggestions(missing_keywords):
    suggestions = []

    for skill in list(missing_keywords)[:5]:
        suggestions.append(
            f"Consider adding measurable experience related to '{skill}' in your resume."
        )

    return suggestions
