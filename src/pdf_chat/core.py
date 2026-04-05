"""Core business logic for PDF Chat Assistant."""

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Ensure common/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from common.llm_client import chat, check_ollama_running  # noqa: E402

SYSTEM_PROMPT = (
    "You are a helpful PDF document assistant. Answer questions based ONLY on "
    "the provided document context. If the answer is not in the context, say so. "
    "Be concise, accurate, and cite relevant parts of the document when possible."
)

DEFAULT_CHUNK_SIZE = 2000
DEFAULT_CHUNK_OVERLAP = 200


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file using PyPDF2."""
    from PyPDF2 import PdfReader

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    text_parts: list[str] = []
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text_parts.append(f"[Page {i + 1}]\n{page_text}")
    logger.info("Extracted %d pages from %s", len(text_parts), pdf_path)
    return "\n\n".join(text_parts)


def extract_text_from_multiple_pdfs(pdf_paths: list[str]) -> dict[str, str]:
    """Extract text from multiple PDF files.

    Returns:
        Dict mapping filename to extracted text.
    """
    results: dict[str, str] = {}
    for path in pdf_paths:
        name = os.path.basename(path)
        try:
            results[name] = extract_text_from_pdf(path)
            logger.info("Loaded PDF: %s", name)
        except Exception as exc:
            logger.error("Failed to load %s: %s", name, exc)
    return results


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks for context windows."""
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def find_relevant_chunks(
    question: str, chunks: list[str], top_k: int = 3
) -> list[str]:
    """Find the most relevant chunks for a question using keyword matching."""
    question_words = set(question.lower().split())
    scored = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = sum(1 for word in question_words if word in chunk_lower)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def ask_question(
    question: str,
    context_chunks: list[str],
    history: list[dict],
    model: str = "gemma4",
    temperature: float = 0.7,
) -> str:
    """Ask a question about the PDF using relevant context."""
    context = "\n\n---\n\n".join(context_chunks)
    user_message = (
        f"Document Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer based on the document context above."
    )
    messages = history + [{"role": "user", "content": user_message}]
    return chat(messages, model=model, system_prompt=SYSTEM_PROMPT, temperature=temperature)
