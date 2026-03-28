"""WebSocket server for communication with the Chrome extension.

The Python side runs as the WebSocket server. The Chrome extension
connects as a client. Commands are sent as JSON, responses are
correlated by command ID using asyncio.Future.

Example:
    server = WebSocketServer(port=9819)
    await server.start()
    await server.wait_for_connection(timeout=30)

    response = await server.send_command(
        action="click",
        tab_id=42,
        params={"selector": "#btn", "selectorType": "css"},
        timeout=10,
    )

    await server.stop()
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("pywebflx")

import websockets
from websockets.asyncio.server import Server, ServerConnection

from pywebflx.protocol import (
    Command,
    Response,
    Event,
    build_command,
    parse_message,
)
from pywebflx.exceptions import (
    ExtensionNotConnectedError,
    ConnectionLostError,
)


class WebSocketServer:
    """WebSocket server that manages communication with the Chrome extension."""

    def __init__(self, port: int = 9819):
        self.port = port
        self._server: Server | None = None
        self._client: ServerConnection | None = None
        self._pending: dict[str, asyncio.Future[Response]] = {}
        self._event_handlers: list[Callable[[Event], Any]] = []
        self._connection_event = asyncio.Event()
        self._listener_task: asyncio.Task | None = None

    @property
    def is_running(self) -> bool:
        return self._server is not None

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    async def start(self) -> None:
        """Start the WebSocket server. No-op if already running."""
        if self._server is not None:
            return
        self._server = await websockets.serve(
            self._handle_client,
            "localhost",
            self.port,
        )
        # If port was 0, get the actual assigned port
        if self.port == 0:
            for sock in self._server.sockets:
                self.port = sock.getsockname()[1]
                break

    async def stop(self) -> None:
        """Stop the WebSocket server and disconnect any client."""
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None

        if self._client:
            await self._client.close()
            self._client = None

        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        self._connection_event.clear()

        # Reject all pending commands
        for future in self._pending.values():
            if not future.done():
                future.set_exception(
                    ConnectionLostError("Server stopped")
                )
        self._pending.clear()

    async def wait_for_connection(self, timeout: float = 30) -> None:
        """Wait for the Chrome extension to connect.

        Raises:
            ExtensionNotConnectedError: If no connection within timeout.
        """
        try:
            await asyncio.wait_for(
                self._connection_event.wait(),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise ExtensionNotConnectedError(port=self.port, timeout=timeout)

    async def send_command(
        self,
        action: str,
        tab_id: int | None = None,
        params: dict[str, Any] | None = None,
        timeout: float = 10,
    ) -> Response:
        """Send a command to the Chrome extension and wait for response.

        Raises:
            ExtensionNotConnectedError: If no extension is connected.
            ConnectionLostError: If connection drops while waiting.
            asyncio.TimeoutError: If response not received within timeout.
        """
        if not self.is_connected:
            raise ExtensionNotConnectedError(port=self.port)

        cmd = build_command(action=action, tab_id=tab_id, params=params or {})
        future: asyncio.Future[Response] = asyncio.get_event_loop().create_future()
        self._pending[cmd.id] = future

        try:
            await self._client.send(cmd.to_json())
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending.pop(cmd.id, None)
            raise
        except websockets.ConnectionClosed:
            self._pending.pop(cmd.id, None)
            raise ConnectionLostError("WebSocket closed while waiting for response")

    def on_event(self, handler: Callable[[Event], Any]) -> None:
        """Register a handler for unsolicited extension events."""
        self._event_handlers.append(handler)

    async def _handle_client(self, websocket: ServerConnection) -> None:
        """Handle a new client connection from the Chrome extension."""
        self._client = websocket
        self._connection_event.set()

        try:
            async for raw_message in websocket:
                await self._dispatch_message(str(raw_message))
        except websockets.ConnectionClosed:
            pass
        finally:
            self._client = None
            self._connection_event.clear()
            for future in self._pending.values():
                if not future.done():
                    future.set_exception(
                        ConnectionLostError("Extension disconnected")
                    )
            self._pending.clear()

    async def _dispatch_message(self, raw: str) -> None:
        """Parse and dispatch an incoming message."""
        try:
            msg = parse_message(raw)
        except ValueError:
            return

        if isinstance(msg, Response):
            future = self._pending.pop(msg.id, None)
            if future and not future.done():
                future.set_result(msg)
        elif isinstance(msg, Event):
            for handler in self._event_handlers:
                try:
                    result = handler(msg)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception:
                    pass
