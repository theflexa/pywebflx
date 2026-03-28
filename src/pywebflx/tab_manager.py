"""Tab management for PyWebFlx.

Handles finding existing tabs by title/URL, creating new tabs,
and the find_or_open logic (equivalent to UiPath's if_not_open).

Example:
    mgr = TabManager(connection)
    tab = await mgr.find_or_open(
        title="Portal Sicoob",
        url="sicoob.com.br",
        if_not_open="https://portal.sicoob.com.br/login"
    )
    tab_id = tab["id"]
"""

from __future__ import annotations

from typing import Any

from pywebflx.connection import WebSocketServer
from pywebflx.exceptions import TabNotFoundError, BrowserNotFoundError


class TabManager:
    """Manages Chrome tab discovery and creation."""

    def __init__(self, conn: WebSocketServer):
        self._conn = conn

    async def find_tab(
        self,
        title: str | None = None,
        url: str | None = None,
    ) -> dict[str, Any]:
        """Find an open tab matching the given title and/or URL.

        Raises:
            TabNotFoundError: If no matching tab is found.
        """
        params = {}
        if title:
            params["title"] = title
        if url:
            params["url"] = url

        response = await self._conn.send_command(
            action="find_tabs",
            params=params,
            timeout=10,
        )

        tabs = response.data
        if not tabs:
            raise TabNotFoundError(title=title, url=url)

        return tabs[0]

    async def create_tab(self, url: str) -> dict[str, Any]:
        """Create a new tab with the given URL."""
        response = await self._conn.send_command(
            action="create_tab",
            params={"url": url},
            timeout=30,
        )
        return response.data

    async def find_or_open(
        self,
        title: str | None = None,
        url: str | None = None,
        if_not_open: str | None = None,
    ) -> dict[str, Any]:
        """Find a tab, or open a new one if not found.

        Raises:
            BrowserNotFoundError: If tab not found and no fallback URL.
        """
        try:
            return await self.find_tab(title=title, url=url)
        except TabNotFoundError:
            if if_not_open:
                return await self.create_tab(if_not_open)
            raise BrowserNotFoundError(title=title, url=url)
