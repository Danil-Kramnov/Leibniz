from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config import CATEGORIES

# Load model once at startup
model = None
category_embeddings = None


def init_model():
    global model, category_embeddings
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        category_embeddings = {
            cat: model.encode(desc) for cat, desc in CATEGORIES.items()
        }


def categorize_book(title, author=""):
    init_model()

    text = f"{title} {author}"
    book_embedding = model.encode(text)

    similarities = {
        cat: cosine_similarity([book_embedding], [emb])[0][0]
        for cat, emb in category_embeddings.items()
    }

    best_category = max(similarities, key=similarities.get)
    confidence = similarities[best_category]

    if confidence < 0.4:
        return "Uncategorized", float(confidence)

    return best_category, float(confidence)
