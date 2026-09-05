import asyncio
import json
import logging
import re
import time
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .config import settings
from .db import engine, get_db, init_db
from .models import Artifact, Message, Session, TranscriptChunk
from .providers.factory import get_provider
from .retrieval import retrieve
from .schemas import ChatRequest, SessionCreate, SessionOut
from .skills.ship30_writer import Ship30Writer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("lenny")
ship30_writer = Ship30Writer()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(title="Lenny Growth Assistant", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[item.strip() for item in settings.cors_origins.split(",")],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
async def health(db: AsyncSession = Depends(get_db)):
    checks = {"api": "ok", "database": "ok", "ollama": "unknown", "knowledge_base": "empty"}
    try:
        await db.execute(select(func.count(TranscriptChunk.id)))
        count = (await db.execute(select(func.count(TranscriptChunk.id)))).scalar_one()
        checks["knowledge_base"] = "ready" if count else "empty"
    except Exception as exc:
        checks["database"] = f"error: {exc.__class__.__name__}"
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            checks["ollama"] = "ok" if response.is_success else "unavailable"
    except Exception:
        checks["ollama"] = "unavailable"
    return {"status": "ok", "checks": checks}


@app.post("/api/sessions", response_model=SessionOut)
async def create_session(payload: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = Session(title=payload.title)
    db.add(session)
    await db.commit()
    result = await db.execute(select(Session).options(selectinload(Session.messages)).where(Session.id == session.id))
    return result.scalar_one()


@app.get("/api/sessions/{session_id}", response_model=SessionOut)
async def get_session(session_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Session).options(selectinload(Session.messages)).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    return session


def grounded_prompt(question: str, history: list[Message], sources: list[dict]) -> str:
    context = "\n\n".join(f"[{source['episode']} | {source['guest']} | {source['reference']}]\n{source['text']}" for source in sources)
    prior = "\n".join(f"{item.role}: {item.content}" for item in history[-6:])
    return f"""You are Lenny Growth Assistant. Answer only from the transcript context below. Never invent guests, episodes, dates, timestamps, or facts. If the context is insufficient, say exactly: I do not have sufficient information in Lenny's podcast archive to answer this. Cite useful claims using [Episode: <episode>, Guest: <guest>, <timestamp/topic>]. Keep the answer practical and concise. If asked to write an essay or article, use these instructions: {ship30_writer.prompt_suffix()} If asked for an artifact, wrap it as <artifact type=\"markdown\" title=\"Growth Framework\">...</artifact> or <artifact type=\"html\" title=\"Growth Framework\"><style>...</style>...</artifact> as requested.

Conversation:
{prior}

Transcript context:
{context or '(no matching transcript context)'}

Question: {question}"""


@app.post("/api/chat")
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Session).options(selectinload(Session.messages)).where(Session.id == payload.session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    retrieval_started = time.perf_counter()
    sources = await retrieve(db, payload.message)
    logger.info("retrieval query=%r sources=%d latency_ms=%.1f", payload.message[:80], len(sources), (time.perf_counter() - retrieval_started) * 1000)
    user_message = Message(session_id=session.id, role="user", content=payload.message, sources=[])
    db.add(user_message)
    await db.commit()
    prompt = grounded_prompt(payload.message, session.messages, sources)
    provider = get_provider(payload.provider)

    async def events():
        full = []
        try:
            yield f"data: {json.dumps({'type': 'status', 'value': 'Retrieving transcript context...'})}\n\n"
            for source in sources:
                yield f"data: {json.dumps({'type': 'source', 'value': {k: source[k] for k in ('episode', 'guest', 'reference', 'preview')}})}\n\n"
            yield f"data: {json.dumps({'type': 'status', 'value': 'Writing grounded response...'})}\n\n"
            async for token in provider.stream(prompt):
                full.append(token)
                yield f"data: {json.dumps({'type': 'token', 'value': token})}\n\n"
            answer = "".join(full)
            if not answer:
                answer = "I do not have sufficient information in Lenny's podcast archive to answer this."
            if sources and "[Episode:" not in answer:
                source = sources[0]
                answer += f"\n\n[Episode: {source['episode']}, Guest: {source['guest']}, {source['reference']}]"
            logger.info("provider=%s session_id=%s latency_ms=%.1f", payload.provider, session.id, (time.perf_counter() - retrieval_started) * 1000)
            async with db.begin():
                assistant = Message(session_id=session.id, role="assistant", content=answer, sources=sources)
                db.add(assistant)
                await db.flush()
                for match in re.finditer(r"<artifact type=\"(markdown|html)\" title=\"([^\"]+)\">(.*?)</artifact>", answer, re.S):
                    db.add(Artifact(message_id=assistant.id, artifact_type=match.group(1), content=match.group(3).strip()))
            yield f"data: {json.dumps({'type': 'done', 'value': {'answer': answer, 'sources': sources}})}\n\n"
        except Exception as exc:
            logger.exception("chat provider failure")
            yield f"data: {json.dumps({'type': 'error', 'value': str(exc)})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@app.get("/api/sessions/{session_id}/artifacts")
async def artifacts(session_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Artifact).join(Message).where(Message.session_id == session_id).order_by(Artifact.created_at.desc()))
    return [{"id": item.id, "type": item.artifact_type, "content": item.content} for item in result.scalars()]
