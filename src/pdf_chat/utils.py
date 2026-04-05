"""Helper utilities for PDF Chat Assistant."""

import logging
import os
import re
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """Convert a string into a safe filename."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    return name.strip()[:100]


def ensure_dir(path: str | Path) -> Path:
    """Create directory if it doesn't exist and return the Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def export_chat_to_markdown(
    pdf_name: str,
    history: list[dict],
    output_dir: str = "exports",
) -> str:
    """Export conversation history to a Markdown file.

    Returns:
        The path to the exported file.
    """
    out = ensure_dir(output_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = sanitize_filename(Path(pdf_name).stem)
    filepath = out / f"chat_{safe_name}_{timestamp}.md"

    lines = [
        f"# Chat Export — {pdf_name}",
        f"*Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
        "---\n",
    ]
    for msg in history:
        role = msg["role"].capitalize()
        lines.append(f"### {role}\n")
        lines.append(msg["content"] + "\n")
        lines.append("---\n")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Chat exported to %s", filepath)
    return str(filepath)


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text with ellipsis if it exceeds *max_length*."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
