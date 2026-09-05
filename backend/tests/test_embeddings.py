from app.embeddings import embed, similarity


def test_embedding_is_deterministic_and_normalized():
    vector = embed("growth loops")
    assert vector == embed("growth loops")
    assert round(similarity(vector, vector), 5) == 1
