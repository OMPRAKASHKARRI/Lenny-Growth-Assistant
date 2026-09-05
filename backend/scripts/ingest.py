"""Ingest .txt/.md transcripts. Uses local deterministic vectors for an offline demo."""
import asyncio
import re
from pathlib import Path
from sqlalchemy import delete
from app.db import SessionLocal, init_db
from app.embeddings import embed
from app.models import TranscriptChunk


def chunks(text: str, words: int = 650, overlap: int = 100):
    tokens = text.split()
    for start in range(0, len(tokens), max(1, words - overlap)):
        piece = " ".join(tokens[start:start + words])
        if piece:
            yield piece
        if start + words >= len(tokens):
            break


async def main():
    await init_db()
    project_root = Path(__file__).parents[2]
    roots = [project_root / "agent_transcripts", project_root / "data" / "transcripts"]
    async with SessionLocal() as db:
        await db.execute(delete(TranscriptChunk))
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.suffix.lower() not in {".txt", ".md"}:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                title = path.stem.replace("_", " ").replace("-", " ").title()
                guest = "Unknown guest"
                match = re.search(r"(?:guest|with)\s*[:\-]\s*([^\n]+)", text[:1000], re.I)
                if match:
                    guest = match.group(1).strip()
                for index, piece in enumerate(chunks(text)):
                    vector = embed(piece)
                    db.add(TranscriptChunk(episode_title=title, guest_name=guest, timestamp_ref=f"Chunk {index + 1}", chunk_text=piece, embedding=vector, metadata_json={"source": str(path.relative_to(project_root))}))
        await db.commit()
    print("Transcript ingestion complete")


if __name__ == "__main__":
    asyncio.run(main())
