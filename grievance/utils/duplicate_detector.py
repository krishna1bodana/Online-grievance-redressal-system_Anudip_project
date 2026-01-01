from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from grievance.models import Grievance


SIMILARITY_THRESHOLD = 0.65  # 65% similarity


def find_duplicate_grievance(new_text, category):
    """
    Returns a similar grievance if found, else None
    """

    existing = Grievance.objects.filter(
        category=category
    ).values_list('description', flat=True)

    if not existing:
        return None

    corpus = list(existing) + [new_text]

    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2)
    )

    tfidf_matrix = vectorizer.fit_transform(corpus)

    similarities = cosine_similarity(
        tfidf_matrix[-1],
        tfidf_matrix[:-1]
    )[0]

    max_similarity = max(similarities)

    if max_similarity >= SIMILARITY_THRESHOLD:
        index = similarities.argmax()
        return Grievance.objects.filter(
            category=category
        )[index]

    return None
