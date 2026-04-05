"""
Demo script for Pdf Chat Assistant
Shows how to use the core module programmatically.

Usage:
    python examples/demo.py
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pdf_chat.core import extract_text_from_pdf, extract_text_from_multiple_pdfs, chunk_text, find_relevant_chunks, ask_question


def main():
    """Run a quick demo of Pdf Chat Assistant."""
    print("=" * 60)
    print("🚀 Pdf Chat Assistant - Demo")
    print("=" * 60)
    print()
    # Extract all text from a PDF file using PyPDF2.
    print("📝 Example: extract_text_from_pdf()")
    result = extract_text_from_pdf(
        pdf_path="sample.pdf"
    )
    print(f"   Result: {result}")
    print()
    # Extract text from multiple PDF files.
    print("📝 Example: extract_text_from_multiple_pdfs()")
    result = extract_text_from_multiple_pdfs(
        pdf_paths=["item1", "item2", "item3"]
    )
    print(f"   Result: {result}")
    print()
    # Split text into overlapping chunks for context windows.
    print("📝 Example: chunk_text()")
    result = chunk_text(
        text="The quick brown fox jumps over the lazy dog. This is a sample text for demonstration purposes."
    )
    print(f"   Result: {result}")
    print()
    # Find the most relevant chunks for a question using keyword matching.
    print("📝 Example: find_relevant_chunks()")
    result = find_relevant_chunks(
        question="What are the key points in this document?",
        chunks=["item1", "item2", "item3"]
    )
    print(f"   Result: {result}")
    print()
    print("✅ Demo complete! See README.md for more examples.")


if __name__ == "__main__":
    main()
