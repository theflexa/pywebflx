"""Tests for the WebSocket server connection module."""

import asyncio
import json

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pywebflx.connection import WebSocketServer
from pywebflx.protocol import Response, Event
from pywebflx.exceptions import ExtensionNotConnectedError, ConnectionLostError


class TestWebSocketServerLifecycle:
    """Test server start/stop lifecycle."""

    @pytest.fixture
    def server(self):
        return WebSocketServer(port=0)  # port=0 for OS-assigned port

    async def test_start_and_stop(self, server):
        await server.start()
        assert server.is_running
        await server.stop()
        assert not server.is_running

    async def test_stop_without_start_is_safe(self, server):
        await server.stop()  # should not raise

    async def test_start_twice_is_safe(self, server):
        await server.start()
        await server.start()  # should not raise
        assert server.is_running
        await server.stop()


class TestWebSocketServerConnection:
    """Test extension client connection handling."""

    async def test_wait_for_connection_timeout(self):
        server = WebSocketServer(port=0)
        await server.start()
        try:
            with pytest.raises(ExtensionNotConnectedError):
                await server.wait_for_connection(timeout=0.5)
        finally:
            await server.stop()

    async def test_is_connected_false_when_no_client(self):
        server = WebSocketServer(port=0)
        await server.start()
        assert not server.is_connected
        await server.stop()


class TestWebSocketServerSendReceive:
    """Test command sending and response receiving."""

    async def test_send_command_without_connection_raises(self):
        server = WebSocketServer(port=0)
        await server.start()
        try:
            with pytest.raises(ExtensionNotConnectedError):
                await server.send_command("click", tab_id=1, params={}, timeout=0.5)
        finally:
            await server.stop()
