"""JSON protocol for communication between Python and Chrome extension.

Commands flow from Python to the extension, responses flow back.
Events are unsolicited messages from the extension (e.g., tab_closed).

Command format (Python -> Extension):
    {"id": "cmd_123", "action": "click", "tabId": 42, "params": {...}}

Response format (Extension -> Python):
    {"id": "cmd_123", "success": true, "data": ...}
    {"id": "cmd_123", "success": false, "error": "ErrorType", "message": "..."}

Event format (Extension -> Python):
    {"event": "tab_closed", "tabId": 42}
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Command:
    """A command to be sent to the Chrome extension."""

    id: str
    action: str
    tab_id: int | None
    params: dict[str, Any]

    def to_json(self) -> str:
        """Serialize command to JSON string for WebSocket transmission."""
        data: dict[str, Any] = {
            "id": self.id,
            "action": self.action,
            "tabId": self.tab_id,
            "params": self.params,
        }
        return json.dumps(data)


@dataclass
class Response:
    """A response received from the Chrome extension."""

    id: str
    success: bool
    data: Any = None
    error: str | None = None
    message: str | None = None


@dataclass
class Event:
    """An unsolicited event from the Chrome extension."""

    event: str
    tab_id: int | None = None
    data: dict[str, Any] = field(default_factory=dict)


def build_command(
    action: str,
    params: dict[str, Any],
    tab_id: int | None = None,
) -> Command:
    """Build a new Command with a unique ID."""
    cmd_id = f"cmd_{uuid.uuid4().hex[:12]}"
    return Command(id=cmd_id, action=action, tab_id=tab_id, params=params)


def parse_message(raw: str) -> Response | Event:
    """Parse a JSON message from the Chrome extension.

    Raises:
        ValueError: If the JSON is invalid or doesn't match any known format.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from extension: {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object, got {type(data).__name__}")

    # Event: has "event" key
    if "event" in data:
        return Event(
            event=data["event"],
            tab_id=data.get("tabId"),
            data={k: v for k, v in data.items() if k not in ("event", "tabId")},
        )

    # Response: has "id" and "success" keys
    if "id" in data and "success" in data:
        return Response(
            id=data["id"],
            success=data["success"],
            data=data.get("data"),
            error=data.get("error"),
            message=data.get("message"),
        )

    raise ValueError(f"Unknown message format: {list(data.keys())}")
