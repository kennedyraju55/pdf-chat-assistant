"""Tests for PDF Chat Assistant CLI."""

import sys
import os
from unittest.mock import patch

from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.pdf_chat.cli import main


class TestCLI:
    """Tests for the CLI interface."""

    @patch("src.pdf_chat.core.check_ollama_running", return_value=False)
    def test_cli_exits_when_ollama_down(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, ["--pdf", __file__])
        assert result.exit_code != 0
