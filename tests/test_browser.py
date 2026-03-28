"""Tests for BrowserContext and use_browser."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pywebflx.browser import BrowserContext, use_browser
from pywebflx.config import PyWebFlxConfig
from pywebflx.protocol import Response
from pywebflx.exceptions import BrowserNotFoundError


class TestBrowserContextInit:
    """Test BrowserContext creation and properties."""

    def test_has_tab_id(self):
        conn = AsyncMock()
        config = PyWebFlxConfig()
        ctx = BrowserContext(conn=conn, tab_id=42, config=config)
        assert ctx._tab_id == 42

    def test_has_config(self):
        conn = AsyncMock()
        config = PyWebFlxConfig(default_timeout=20)
        ctx = BrowserContext(conn=conn, tab_id=1, config=config)
        assert ctx._config.default_timeout == 20


class TestUseBrowser:
    """Test use_browser context manager."""

    async def test_use_browser_finds_tab(self):
        with patch("pywebflx.browser.WebSocketServer") as MockServer, \
             patch("pywebflx.browser.TabManager") as MockTabMgr:
            mock_server = AsyncMock()
            MockServer.return_value = mock_server
            mock_server.is_connected = True

            mock_mgr = AsyncMock()
            MockTabMgr.return_value = mock_mgr
            mock_mgr.find_or_open.return_value = {"id": 42, "title": "Portal", "url": "https://sicoob.com.br"}

            async with use_browser(title="Portal") as browser:
                assert browser._tab_id == 42

    async def test_use_browser_stops_server_on_exit(self):
        with patch("pywebflx.browser.WebSocketServer") as MockServer, \
             patch("pywebflx.browser.TabManager") as MockTabMgr:
            mock_server = AsyncMock()
            MockServer.return_value = mock_server
            mock_server.is_connected = True

            mock_mgr = AsyncMock()
            MockTabMgr.return_value = mock_mgr
            mock_mgr.find_or_open.return_value = {"id": 1, "title": "T", "url": "u"}

            async with use_browser(url="example.com") as browser:
                pass

            mock_server.stop.assert_called_once()
