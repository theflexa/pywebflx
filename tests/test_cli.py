"""Tests for the PyWebFlx CLI."""

from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from pywebflx.cli import main


class TestCLI:
    """Test CLI commands."""

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_install_extension_shows_instructions(self):
        runner = CliRunner()
        result = runner.invoke(main, ["install-extension"])
        assert result.exit_code == 0
        assert "extension" in result.output.lower()

    def test_check_without_server(self):
        runner = CliRunner()
        result = runner.invoke(main, ["check"])
        # Should show that extension is not connected
        assert result.exit_code == 0 or result.exit_code == 1
        assert "extensao" in result.output.lower() or "extension" in result.output.lower()
