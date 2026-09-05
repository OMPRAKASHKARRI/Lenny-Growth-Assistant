import pytest
from app.db import SessionLocal, init_db
from app.models import TranscriptChunk
from app.retrieval import retrieve
from app.embeddings import embed


@pytest.mark.asyncio
async def test_retrieval_returns_relevant_chunk():
    await init_db()
    async with SessionLocal() as db:
        db.add(TranscriptChunk(episode_title="Test Episode", guest_name="Test Guest", timestamp_ref="Chunk 1", chunk_text="Retention shows whether a product becomes a habit.", embedding=embed("Retention shows whether a product becomes a habit.")))
        await db.commit()
        results = await retrieve(db, "Why does retention matter?")
    assert results
    assert results[0]["guest"] == "Test Guest"
