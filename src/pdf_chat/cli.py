"""Click CLI interface for PDF Chat Assistant."""

import sys
import logging

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import load_config, setup_logging
from .core import (
    check_ollama_running,
    extract_text_from_pdf,
    extract_text_from_multiple_pdfs,
    chunk_text,
    find_relevant_chunks,
    ask_question,
)
from .utils import export_chat_to_markdown

logger = logging.getLogger(__name__)
console = Console()


@click.command()
@click.option("--pdf", required=True, multiple=True, type=click.Path(exists=True), help="Path(s) to PDF file(s)")
@click.option("--config", "config_path", default=None, type=click.Path(), help="Path to config.yaml")
@click.option("--export", "export_chat", is_flag=True, help="Export chat history on exit")
def main(pdf: tuple[str, ...], config_path: str | None, export_chat: bool):
    """PDF Chat Assistant - Ask questions about your PDF documents."""
    cfg = load_config(config_path)
    setup_logging(cfg)

    console.print(
        Panel.fit(
            "[bold cyan]📄 PDF Chat Assistant[/bold cyan]\n"
            "Ask questions about your PDF documents",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    chunk_cfg = cfg.get("chunking", {})
    model_cfg = cfg.get("model", {})

    # Load PDFs
    all_chunks: list[str] = []
    pdf_names: list[str] = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
        prog.add_task("Extracting text from PDF(s)...", total=None)
        for pdf_path in pdf:
            text = extract_text_from_pdf(pdf_path)
            if text.strip():
                chunks = chunk_text(
                    text,
                    chunk_size=chunk_cfg.get("chunk_size", 2000),
                    overlap=chunk_cfg.get("chunk_overlap", 200),
                )
                all_chunks.extend(chunks)
                pdf_names.append(pdf_path)

    if not all_chunks:
        console.print("[red]❌ No text could be extracted from the PDF(s).[/red]")
        sys.exit(1)

    console.print(f"[green]✅ Loaded {len(pdf_names)} PDF(s) — {len(all_chunks)} chunks total[/green]")
    console.print("[dim]Commands: 'quit' to exit | 'export' to save chat | 'clear' to reset history[/dim]\n")

    history: list[dict] = []

    while True:
        try:
            question = Prompt.ask("[bold yellow]❓ Your question[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        cmd = question.lower().strip()
        if cmd in ("quit", "exit", "q"):
            break
        if cmd == "export":
            path = export_chat_to_markdown(
                ", ".join(pdf_names), history, cfg.get("export", {}).get("output_dir", "exports")
            )
            console.print(f"[green]✅ Chat exported to {path}[/green]")
            continue
        if cmd == "clear":
            history.clear()
            console.print("[yellow]🔄 Conversation history cleared.[/yellow]")
            continue
        if not question.strip():
            continue

        relevant = find_relevant_chunks(question, all_chunks, top_k=chunk_cfg.get("top_k", 3))

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
            prog.add_task("Thinking...", total=None)
            answer = ask_question(
                question,
                relevant,
                history,
                model=model_cfg.get("name", "gemma4"),
                temperature=model_cfg.get("temperature", 0.7),
            )

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

        console.print()
        console.print(Panel(Markdown(answer), title="[bold green]Answer[/bold green]", border_style="green"))
        console.print()

    if export_chat and history:
        path = export_chat_to_markdown(
            ", ".join(pdf_names), history, cfg.get("export", {}).get("output_dir", "exports")
        )
        console.print(f"[green]✅ Chat exported to {path}[/green]")

    console.print("[bold cyan]👋 Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
