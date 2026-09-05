from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .embeddings import embed, similarity
from .models import TranscriptChunk


async def retrieve(db: AsyncSession, query: str, limit: int = 5) -> list[dict]:
    query_vector = embed(query)
    dialect = db.bind.dialect.name if db.bind else "sqlite"
    if dialect == "postgresql":
        distance = TranscriptChunk.embedding.op("<=>")(query_vector)
        rows = (await db.execute(select(TranscriptChunk, distance.label("distance")).where(TranscriptChunk.embedding.is_not(None)).order_by(distance).limit(limit))).all()
        ranked = [(1 - float(distance), row) for row, distance in rows]
        if not ranked:
            rows = (await db.execute(select(TranscriptChunk))).scalars().all()
            ranked = sorted(((similarity(query_vector, embed(row.chunk_text)), row) for row in rows), key=lambda item: item[0], reverse=True)
    else:
        rows = (await db.execute(select(TranscriptChunk))).scalars().all()
        ranked = sorted(((similarity(query_vector, row.embedding or embed(row.chunk_text)), row) for row in rows), key=lambda item: item[0], reverse=True)
    return [
        {"episode": row.episode_title, "guest": row.guest_name, "reference": row.timestamp_ref,
         "preview": row.chunk_text[:240], "text": row.chunk_text, "score": round(score, 3)}
        for score, row in ranked[:limit] if score >= 0.05
    ]
