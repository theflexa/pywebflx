"""Tests for PyWebFlx logging system."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from pywebflx.logging import configure_logging, _logged_action, _format_log_message


class TestFormatLogMessage:
    """Test log message formatting."""

    def test_success_message(self):
        msg = _format_log_message(
            action="browser.click",
            selector="#btn-salvar",
            tab_id=42,
            status="success",
            duration_ms=120,
        )
        assert "[browser.click]" in msg
        assert "#btn-salvar" in msg
        assert "tab:42" in msg
        assert "success" in msg
        assert "120ms" in msg

    def test_retry_message(self):
        msg = _format_log_message(
            action="browser.click",
            selector="#btn",
            tab_id=42,
            status="retry",
            attempt=1,
            max_attempts=3,
            error_name="ElementNotInteractableError",
        )
        assert "retry 1/3" in msg
        assert "ElementNotInteractableError" in msg

    def test_failure_message(self):
        msg = _format_log_message(
            action="browser.click",
            selector="#btn",
            tab_id=42,
            status="failed",
            error_name="ElementNotFoundError",
        )
        assert "failed" in msg
        assert "ElementNotFoundError" in msg

    def test_success_with_extra_info(self):
        msg = _format_log_message(
            action="browser.type_into",
            selector="#email",
            tab_id=42,
            status="success",
            duration_ms=85,
            extra='"joao@sicoob.com.br"',
        )
        assert '"joao@sicoob.com.br"' in msg

    def test_success_with_retry_info(self):
        msg = _format_log_message(
            action="browser.click",
            selector="#btn",
            tab_id=42,
            status="success",
            duration_ms=340,
            attempt=2,
        )
        assert "retry 2" in msg
        assert "340ms" in msg


class TestLoggedActionDecorator:
    """Test the @_logged_action decorator."""

    async def test_decorator_preserves_return_value(self):
        class FakeBrowser:
            _config = MagicMock()
            _config.resolve.return_value = "INFO"
            _tab_id = 42

            @_logged_action("browser.get_text")
            async def get_text(self, selector, **kwargs):
                return "Hello World"

        browser = FakeBrowser()
        result = await browser.get_text("#title")
        assert result == "Hello World"

    async def test_decorator_reraises_exceptions(self):
        class FakeBrowser:
            _config = MagicMock()
            _config.resolve.return_value = "INFO"
            _tab_id = 42

            @_logged_action("browser.click")
            async def click(self, selector, **kwargs):
                raise ValueError("test error")

        browser = FakeBrowser()
        with pytest.raises(ValueError, match="test error"):
            await browser.click("#btn")


class TestConfigureLogging:
    """Test configure_logging function."""

    def test_configure_with_level(self):
        configure_logging(level="DEBUG")
        configure_logging(level="INFO")
        configure_logging(level="DISABLED")

    def test_configure_with_sink(self):
        import tempfile, os
        fd, log_file = tempfile.mkstemp(suffix=".log")
        os.close(fd)
        try:
            configure_logging(level="DEBUG", sink=log_file)
        finally:
            configure_logging(level="DISABLED")
            os.unlink(log_file)

    def test_configure_with_custom_handler(self):
        messages = []
        configure_logging(handler=lambda msg: messages.append(str(msg)))

    def test_configure_with_timestamp_format(self):
        configure_logging(timestamp_format="%H:%M:%S")
