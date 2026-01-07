from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.utils import timezone
from datetime import timedelta
from grievance.models import Grievance

SIMILARITY_THRESHOLD = 0.65  # 65% similarity

def find_duplicate_grievance(new_text, category):
    """
    Returns a similar grievance object if found, else None.
    Uses TF-IDF Vectorization and Cosine Similarity.
    """
    
    # 1. Fetch recent grievances in the same category (Optimization)
    # Checking everything ever filed can be slow; we look at the last 180 days.
    time_threshold = timezone.now() - timedelta(days=180)
    
    existing_queryset = Grievance.objects.filter(
        category=category,
        created_at__gte=time_threshold
    ).only('id', 'description').order_by('id') # Explicit order is critical!

    if not existing_queryset.exists():
        return None

    # 2. Prepare the corpus
    # We keep the IDs in a list to map the similarity index back to a database record
    existing_descriptions = list(existing_queryset.values_list('description', flat=True))
    existing_ids = list(existing_queryset.values_list('id', flat=True))
    
    corpus = existing_descriptions + [new_text]

    # 3. Vectorization
    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),  # Looks at single words and pairs of words
        max_features=5000    # Prevents memory blowup
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # 4. Calculate Similarity
        # Compare the last item (new_text) against all previous items
        similarities = cosine_similarity(
            tfidf_matrix[-1], 
            tfidf_matrix[:-1]
        )[0]

        if len(similarities) == 0:
            return None

        max_idx = similarities.argmax()
        max_val = similarities[max_idx]

        # 5. Result Mapping
        if max_val >= SIMILARITY_THRESHOLD:
            duplicate_id = existing_ids[max_idx]
            return Grievance.objects.get(id=duplicate_id)
            
    except Exception as e:
        # Log error if needed, but don't crash the submission process
        print(f"Duplicate Detection Error: {e}")
        return None

    return None