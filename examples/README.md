# Examples for Pdf Chat Assistant

This directory contains example scripts demonstrating how to use this project.

## Quick Demo

```bash
python examples/demo.py
```

## What the Demo Shows

- **`extract_text_from_pdf()`** — Extract all text from a PDF file using PyPDF2.
- **`extract_text_from_multiple_pdfs()`** — Extract text from multiple PDF files.
- **`chunk_text()`** — Split text into overlapping chunks for context windows.
- **`find_relevant_chunks()`** — Find the most relevant chunks for a question using keyword matching.
- **`ask_question()`** — Ask a question about the PDF using relevant context.

## Prerequisites

- Python 3.10+
- Ollama running with Gemma 4 model
- Project dependencies installed (`pip install -e .`)

## Running

From the project root directory:

```bash
# Install the project in development mode
pip install -e .

# Run the demo
python examples/demo.py
```
