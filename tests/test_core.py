"""Tests for PDF Chat Assistant core logic."""

import pytest
from unittest.mock import patch, MagicMock

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.pdf_chat.core import (
    chunk_text,
    find_relevant_chunks,
    ask_question,
    extract_text_from_pdf,
    SYSTEM_PROMPT,
)


class TestChunkText:
    """Tests for text chunking functionality."""

    def test_short_text_single_chunk(self):
        text = "This is a short text."
        chunks = chunk_text(text, chunk_size=100)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_long_text_multiple_chunks(self):
        text = "A" * 5000
        chunks = chunk_text(text, chunk_size=2000, overlap=200)
        assert len(chunks) > 1
        assert all(len(c) <= 2000 for c in chunks)

    def test_chunk_overlap(self):
        text = "ABCDEFGHIJ" * 100
        chunks = chunk_text(text, chunk_size=200, overlap=50)
        if len(chunks) >= 2:
            end_of_first = chunks[0][-50:]
            start_of_second = chunks[1][:50]
            assert end_of_first == start_of_second


class TestFindRelevantChunks:
    """Tests for relevant chunk finding."""

    def test_finds_matching_chunks(self):
        chunks = [
            "Python is a programming language",
            "Cooking recipes for dinner",
            "Python data science tools",
        ]
        result = find_relevant_chunks("What is Python?", chunks, top_k=2)
        assert len(result) == 2
        assert "Python" in result[0]

    def test_returns_top_k(self):
        chunks = ["chunk1", "chunk2", "chunk3", "chunk4"]
        result = find_relevant_chunks("test", chunks, top_k=2)
        assert len(result) == 2

    def test_empty_chunks(self):
        result = find_relevant_chunks("test", [], top_k=3)
        assert result == []


class TestAskQuestion:
    """Tests for the ask_question function."""

    @patch("src.pdf_chat.core.chat")
    def test_ask_returns_answer(self, mock_chat):
        mock_chat.return_value = "The answer is 42."
        result = ask_question("What is the answer?", ["context chunk"], [])
        assert result == "The answer is 42."
        mock_chat.assert_called_once()

    @patch("src.pdf_chat.core.chat")
    def test_ask_includes_history(self, mock_chat):
        mock_chat.return_value = "Follow-up answer."
        history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
        ]
        result = ask_question("Second question?", ["context"], history)
        assert result == "Follow-up answer."
        call_args = mock_chat.call_args
        messages = call_args[0][0]
        assert len(messages) == 3  # history (2) + new question (1)


class TestExtractTextFromPdf:
    """Tests for PDF text extraction."""

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("nonexistent.pdf")
