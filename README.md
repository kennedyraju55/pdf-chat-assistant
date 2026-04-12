# 📄 PDF Chat Assistant

> Chat with any PDF document using a local LLM — ask questions, get cited answers, and export conversations. 100% private, zero cloud costs.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Local LLM](https://img.shields.io/badge/LLM-Gemma%204%20via%20Ollama-orange.svg)]()
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-brightgreen.svg)]()
[![RAG](https://img.shields.io/badge/RAG-Chunked%20Retrieval-orange.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)

## 🎬 Demo

*Upload a PDF through the Streamlit interface, then ask natural language questions. The assistant retrieves the most relevant passages, generates accurate answers with context, and maintains conversation history — all running locally on your machine.*

> Add a screenshot showing the chat interface with a PDF loaded and a Q&A conversation here.

## 🔥 Why This Exists

We're drowning in PDFs — research papers, contracts, manuals, reports. Finding specific information means scrolling through hundreds of pages or relying on basic Ctrl+F. Cloud-based PDF chat tools require uploading sensitive documents to third-party servers. **PDF Chat Assistant** brings intelligent document Q&A to your local machine — your documents never leave your computer, and there are no API costs or rate limits.

## ✨ Features

- 💬 **Natural language Q&A** — ask questions about any PDF in plain English
- 📖 **Smart chunking** — documents are split into overlapping chunks (2000 chars, 200 overlap) for precise retrieval
- 🔍 **Top-K retrieval** — fetches the 3 most relevant chunks for each question
- 🗂️ **Multi-turn conversation** — maintains chat history for follow-up questions
- 📤 **Export conversations** — save Q&A sessions for reference
- 🖥️ **Three interfaces** — CLI, Streamlit Web UI, and FastAPI REST API
- 📊 **Configurable parameters** — tune chunk size, overlap, top-K, temperature, and max tokens via YAML
- 🐳 **Docker support** — one-command deployment
- ✅ **Test suite** — pytest coverage included
- 🔒 **100% local** — Gemma 4 via Ollama, no cloud APIs, no data transmission

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                          │
│                                                              │
│  ┌─────────┐    ┌──────────────┐    ┌──────────────────┐    │
│  │   CLI   │    │ Streamlit UI │    │  FastAPI REST API │    │
│  │ (click  │    │ (chat-style  │    │  (JSON endpoints) │    │
│  │  + rich)│    │  interface)  │    │                   │    │
│  └────┬────┘    └──────┬───────┘    └────────┬──────────┘    │
│       └───────────────┬┼─────────────────────┘               │
│                       ▼▼                                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                    Core Engine                        │    │
│  │                                                       │    │
│  │  ┌─────────────┐   ┌─────────────┐   ┌───────────┐   │    │
│  │  │  PDF Parser  │──▶│  Chunker    │──▶│  Search   │   │    │
│  │  │  (PyPDF2)    │   │  (overlap)  │   │  (top-K)  │   │    │
│  │  └─────────────┘   └─────────────┘   └─────┬─────┘   │    │
│  │                                             ▼         │    │
│  │                                     ┌──────────────┐  │    │
│  │                                     │  LLM Query   │  │    │
│  │                                     │  + Context    │  │    │
│  │                                     └──────────────┘  │    │
│  └──────────────────────┬───────────────────────────┘    │
│                         ▼                                │
│              ┌──────────────────┐                        │
│              │  Common LLM      │                        │
│              │  Client Module   │                        │
│              └────────┬─────────┘                        │
│                       ▼                                  │
│              ┌──────────────────┐                        │
│              │  Ollama Server   │                        │
│              │  Gemma 4 model   │                        │
│              │  localhost:11434  │                        │
│              └──────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### RAG Pipeline

```
PDF Upload → PyPDF2 Extract → Chunk (2000 chars, 200 overlap)
                                          ↓
User Question → Match against chunks (top 3) → Inject into prompt → LLM → Answer
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.com)** installed and running
- **Gemma 4** model: `ollama pull gemma4`

### Installation

```bash
git clone https://github.com/kennedyraju55/pdf-chat-assistant.git
cd pdf-chat-assistant
pip install -r requirements.txt
pip install -e .
```

### Usage

**CLI:**
```bash
# Chat with a PDF
python -m src.pdf_chat.cli chat --pdf examples/sample.pdf

# Ask a single question
python -m src.pdf_chat.cli ask --pdf examples/sample.pdf --question "What are the key findings?"

# Export conversation
python -m src.pdf_chat.cli chat --pdf examples/sample.pdf --export conversation.txt
```

**Streamlit Web UI:**
```bash
streamlit run src/pdf_chat/web_ui.py
```

**FastAPI REST API:**
```bash
uvicorn src.pdf_chat.api:app --reload
# POST /upload, /ask, /export
```

**Docker:**
```bash
docker-compose up
```

## 📁 Project Structure

```
pdf-chat-assistant/
├── src/
│   └── pdf_chat/
│       ├── __init__.py
│       ├── core.py          # PDF parsing, chunking, RAG Q&A engine
│       ├── cli.py           # Click + Rich CLI with interactive chat mode
│       ├── web_ui.py        # Streamlit chat-style interface
│       ├── api.py           # FastAPI REST endpoints
│       ├── config.py        # YAML configuration loader
│       └── utils.py         # Helper utilities
├── common/
│   └── llm_client.py       # Shared Ollama API wrapper
├── examples/                # Sample PDFs for testing
├── exports/                 # Saved conversation exports
├── tests/                   # pytest test suite
├── docs/                    # Documentation and images
├── config.yaml              # Chunking, model, and export settings
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── setup.py
```

## ⚙️ Configuration

Edit `config.yaml` to tune the RAG pipeline:

```yaml
model:
  name: gemma4
  temperature: 0.7      # Higher = more creative, lower = more precise
  max_tokens: 2048

chunking:
  chunk_size: 2000       # Characters per chunk
  chunk_overlap: 200     # Overlap between chunks for context continuity
  top_k: 3              # Number of chunks retrieved per question

export:
  output_dir: exports    # Where to save conversation exports
```

## 💡 Example Use Cases

- 📚 **Research papers** — "What methodology did the authors use?" / "Summarize the results section"
- 📋 **Contracts** — "What are the termination conditions?" / "Is there a non-compete clause?"
- 📖 **Manuals** — "How do I configure the network settings?" / "What are the safety warnings?"
- 📊 **Reports** — "What was the revenue growth in Q3?" / "List all recommendations"
- 📜 **Legal documents** — "What are my obligations under Section 4?" / "When is the deadline?"

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License — see [LICENSE](LICENSE)

## 👨‍💻 Author

**Nrk Raju Guthikonda**
- 🏢 Senior Software Engineer at Microsoft (Copilot Search Infrastructure)
- 🔗 [GitHub](https://github.com/kennedyraju55) | [LinkedIn](https://www.linkedin.com/in/nrk-raju-guthikonda-504066a8/)
- 🚀 Building 116+ open-source AI tools for real-world impact

---

<p align="center">
  <b>⭐ If this helps you make sense of your PDFs, give it a star!</b>
</p>
