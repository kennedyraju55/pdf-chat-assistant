"""FastAPI REST API for PDF Chat Assistant."""
import os
import sys
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.pdf_chat.core import (
    extract_text_from_pdf,
    chunk_text,
    find_relevant_chunks,
    ask_question,
)

app = FastAPI(
    title="PDF Chat Assistant API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class AskRequest(BaseModel):
    """Request to ask a question about PDF content."""
    question: str
    context_text: str
    chunk_size: int = 2000
    chunk_overlap: int = 200
    top_k: int = 3
    model: str = "gemma4"
    temperature: float = 0.7


class AskResponse(BaseModel):
    """Response with the answer."""
    answer: str
    num_chunks_used: int
    status: str = "success"


class ChunkRequest(BaseModel):
    """Request to chunk text."""
    text: str
    chunk_size: int = 2000
    overlap: int = 200


class ChunkResponse(BaseModel):
    """Chunked text response."""
    chunks: list[str]
    num_chunks: int


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/chunk", response_model=ChunkResponse)
async def chunk_endpoint(request: ChunkRequest):
    """Split text into overlapping chunks."""
    try:
        chunks = chunk_text(request.text, request.chunk_size, request.overlap)
        return ChunkResponse(chunks=chunks, num_chunks=len(chunks))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AskResponse)
async def ask_endpoint(request: AskRequest):
    """Ask a question about PDF content."""
    try:
        chunks = chunk_text(request.context_text, request.chunk_size, request.chunk_overlap)
        relevant = find_relevant_chunks(request.question, chunks, request.top_k)
        answer = ask_question(
            question=request.question,
            context_chunks=relevant,
            history=[],
            model=request.model,
            temperature=request.temperature,
        )
        return AskResponse(answer=answer, num_chunks_used=len(relevant))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
