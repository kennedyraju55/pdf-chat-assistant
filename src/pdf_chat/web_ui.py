"""Streamlit web interface for PDF Chat Assistant."""

import sys
from pathlib import Path

# Ensure common/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st

from .config import load_config, setup_logging
from .core import (
    check_ollama_running,
    extract_text_from_pdf,
    chunk_text,
    find_relevant_chunks,
    ask_question,
)
from .utils import export_chat_to_markdown

# --- Page config ---
# Custom CSS for professional dark theme
st.set_page_config(page_title="PDF Chat Assistant", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { background: linear-gradient(180deg, #0e1117 0%, #1a1a2e 100%); }
    h1 { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem !important; }
    h2 { color: #667eea !important; }
    h3 { color: #a78bfa !important; }
    .stButton>button { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; padding: 0.5rem 2rem; font-weight: 600; transition: transform 0.2s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #1a1a2e; border: 1px solid #333; color: #e0e0e0; border-radius: 8px; }
    .stSelectbox>div>div { background-color: #1a1a2e; border: 1px solid #333; }
    .stMetric { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 1rem; border-radius: 10px; border: 1px solid #333; }
    .css-1d391kg { background-color: #1a1a2e; }
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); }
    .stSuccess { background-color: rgba(102, 126, 234, 0.1); border: 1px solid #667eea; }
    footer { visibility: hidden; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)


def init_state():
    """Initialize session state."""
    defaults = {
        "chunks": [],
        "pdf_names": [],
        "history": [],
        "config": load_config(),
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def sidebar():
    """Render sidebar with settings and file upload."""
    cfg = st.session_state.config
    st.sidebar.title("⚙️ Settings")

    cfg["model"]["name"] = st.sidebar.text_input("Model", value=cfg["model"]["name"])
    cfg["model"]["temperature"] = st.sidebar.slider("Temperature", 0.0, 1.0, cfg["model"]["temperature"], 0.1)
    cfg["chunking"]["chunk_size"] = st.sidebar.number_input("Chunk Size", 500, 8000, cfg["chunking"]["chunk_size"], 100)
    cfg["chunking"]["top_k"] = st.sidebar.number_input("Top-K Chunks", 1, 10, cfg["chunking"]["top_k"])

    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Upload PDFs")
    uploaded = st.sidebar.file_uploader("Choose PDF(s)", type=["pdf"], accept_multiple_files=True)

    if uploaded:
        import tempfile, os
        st.session_state.chunks = []
        st.session_state.pdf_names = []
        for uf in uploaded:
            tmp_path = Path("_uploaded_pdfs") / uf.name
            tmp_path.parent.mkdir(exist_ok=True)
            tmp_path.write_bytes(uf.read())
            try:
                text = extract_text_from_pdf(str(tmp_path))
                if text.strip():
                    chunks = chunk_text(text, cfg["chunking"]["chunk_size"], cfg["chunking"].get("chunk_overlap", 200))
                    st.session_state.chunks.extend(chunks)
                    st.session_state.pdf_names.append(uf.name)
            except Exception as e:
                st.sidebar.error(f"Error reading {uf.name}: {e}")

        if st.session_state.pdf_names:
            st.sidebar.success(f"Loaded {len(st.session_state.pdf_names)} PDF(s), {len(st.session_state.chunks)} chunks")

    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)
    if col1.button("🗑️ Clear Chat"):
        st.session_state.history = []
        st.rerun()
    if col2.button("📥 Export Chat"):
        if st.session_state.history:
            path = export_chat_to_markdown(
                ", ".join(st.session_state.pdf_names),
                st.session_state.history,
            )
            st.sidebar.success(f"Exported to {path}")
        else:
            st.sidebar.warning("No chat history to export.")


def main():
    """Main Streamlit app."""
    init_state()
    setup_logging(st.session_state.config)

    st.title("📄 PDF Chat Assistant")
    st.caption("Upload PDFs and ask questions about their content — powered by a local LLM.")

    sidebar()

    if not st.session_state.chunks:
        st.info("👈 Upload one or more PDF files in the sidebar to get started.")
        return

    # Display chat history
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your PDF(s)..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.history.append({"role": "user", "content": prompt})

        cfg = st.session_state.config
        relevant = find_relevant_chunks(prompt, st.session_state.chunks, top_k=cfg["chunking"]["top_k"])

        with st.spinner("Thinking..."):
            if not check_ollama_running():
                st.error("❌ Ollama is not running. Start it with: `ollama serve`")
                return
            answer = ask_question(
                prompt,
                relevant,
                st.session_state.history[:-1],
                model=cfg["model"]["name"],
                temperature=cfg["model"]["temperature"],
            )

        st.chat_message("assistant").markdown(answer)
        st.session_state.history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
