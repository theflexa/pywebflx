"""Tests for tab management (find, create, track)."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from pywebflx.tab_manager import TabManager
from pywebflx.protocol import Response
from pywebflx.exceptions import TabNotFoundError, BrowserNotFoundError


class TestFindTab:
    """Test finding tabs by title and URL."""

    async def test_find_by_title(self):
        conn = AsyncMock()
        conn.send_command.return_value = Response(
            id="cmd_1", success=True,
            data=[{"id": 42, "title": "Portal Sicoob", "url": "https://sicoob.com.br"}]
        )
        mgr = TabManager(conn)
        tab = await mgr.find_tab(title="Portal Sicoob")
        assert tab["id"] == 42

    async def test_find_by_url(self):
        conn = AsyncMock()
        conn.send_command.return_value = Response(
            id="cmd_1", success=True,
            data=[{"id": 10, "title": "Page", "url": "https://sicoob.com.br/portal"}]
        )
        mgr = TabManager(conn)
        tab = await mgr.find_tab(url="sicoob.com.br")
        assert tab["id"] == 10

    async def test_find_by_title_and_url(self):
        conn = AsyncMock()
        conn.send_command.return_value = Response(
            id="cmd_1", success=True,
            data=[{"id": 7, "title": "Portal", "url": "https://sicoob.com.br"}]
        )
        mgr = TabManager(conn)
        tab = await mgr.find_tab(title="Portal", url="sicoob.com.br")
        assert tab["id"] == 7

    async def test_find_no_match_raises(self):
        conn = AsyncMock()
        conn.send_command.return_value = Response(
            id="cmd_1", success=True, data=[]
        )
        mgr = TabManager(conn)
        with pytest.raises(TabNotFoundError):
            await mgr.find_tab(title="Nonexistent")

    async def test_find_returns_first_match(self):
        conn = AsyncMock()
        conn.send_command.return_value = Response(
            id="cmd_1", success=True,
            data=[
                {"id": 1, "title": "Portal A", "url": "a.com"},
                {"id": 2, "title": "Portal B", "url": "b.com"},
            ]
        )
        mgr = TabManager(conn)
        tab = await mgr.find_tab(title="Portal")
        assert tab["id"] == 1


class TestCreateTab:
    """Test creating new tabs."""

    async def test_create_tab(self):
        conn = AsyncMock()
        conn.send_command.return_value = Response(
            id="cmd_1", success=True,
            data={"id": 99, "title": "", "url": "https://example.com"}
        )
        mgr = TabManager(conn)
        tab = await mgr.create_tab("https://example.com")
        assert tab["id"] == 99
        conn.send_command.assert_called_once_with(
            action="create_tab",
            params={"url": "https://example.com"},
            timeout=30,
        )


class TestFindOrOpen:
    """Test find_or_open with if_not_open fallback."""

    async def test_find_existing_tab(self):
        conn = AsyncMock()
        conn.send_command.return_value = Response(
            id="cmd_1", success=True,
            data=[{"id": 42, "title": "Portal", "url": "https://sicoob.com.br"}]
        )
        mgr = TabManager(conn)
        tab = await mgr.find_or_open(title="Portal", if_not_open="https://sicoob.com.br")
        assert tab["id"] == 42

    async def test_creates_tab_when_not_found(self):
        conn = AsyncMock()
        conn.send_command.side_effect = [
            Response(id="cmd_1", success=True, data=[]),
            Response(id="cmd_2", success=True, data={"id": 99, "title": "", "url": "https://sicoob.com.br"}),
        ]
        mgr = TabManager(conn)
        tab = await mgr.find_or_open(title="Portal", if_not_open="https://sicoob.com.br")
        assert tab["id"] == 99

    async def test_raises_when_not_found_and_no_fallback(self):
        conn = AsyncMock()
        conn.send_command.return_value = Response(id="cmd_1", success=True, data=[])
        mgr = TabManager(conn)
        with pytest.raises(BrowserNotFoundError):
            await mgr.find_or_open(title="Portal")
