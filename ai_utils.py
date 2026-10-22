from sentence_transformers import SentenceTransformer, util

# Lightweight aur fast pre-trained model load kar rahe hain
model = SentenceTransformer('all-MiniLM-L6-v2')

def check_doubt_similarity(new_question: str, existing_questions: list[str], threshold: float = 0.75):
    """
    Check karta hai ki naya question pehle ke questions se kitna match karta hai.
    Agar similarity threshold se zyada hai, toh match return karega.
    """
    if not existing_questions:
        return None, 0.0

    # Questions ko vector embeddings me convert karein
    new_embedding = model.encode(new_question, convert_to_tensor=True)
    existing_embeddings = model.encode(existing_questions, convert_to_tensor=True)

    # Cosine similarity calculate karein
    cosine_scores = util.cos_sim(new_embedding, existing_embeddings)[0]
    
    # Best match find karein
    best_match_idx = int(cosine_scores.argmax())
    best_score = float(cosine_scores[best_match_idx])

    if best_score >= threshold:
        return existing_questions[best_match_idx], best_score
    
    return None, best_score