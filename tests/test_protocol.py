"""Tests for the JSON protocol between Python and Chrome extension."""

import json
import pytest
from pywebflx.protocol import (
    Command,
    Response,
    Event,
    build_command,
    parse_message,
)


class TestBuildCommand:
    """Verify command serialization."""

    def test_click_command(self):
        cmd = build_command(
            action="click",
            tab_id=42,
            params={"selector": "#btn", "selectorType": "css"},
        )
        assert cmd.action == "click"
        assert cmd.tab_id == 42
        assert cmd.params["selector"] == "#btn"
        assert cmd.id.startswith("cmd_")

    def test_command_to_json(self):
        cmd = build_command(action="get_text", tab_id=10, params={"selector": ".title"})
        data = json.loads(cmd.to_json())
        assert data["action"] == "get_text"
        assert data["tabId"] == 10
        assert data["params"]["selector"] == ".title"
        assert "id" in data

    def test_command_ids_are_unique(self):
        cmd1 = build_command(action="click", tab_id=1, params={})
        cmd2 = build_command(action="click", tab_id=1, params={})
        assert cmd1.id != cmd2.id

    def test_command_without_tab_id(self):
        cmd = build_command(action="find_tabs", params={"title": "Portal"})
        data = json.loads(cmd.to_json())
        assert data.get("tabId") is None


class TestParseMessage:
    """Verify response and event parsing."""

    def test_parse_success_response(self):
        raw = json.dumps({"id": "cmd_1", "success": True, "data": "Hello"})
        msg = parse_message(raw)
        assert isinstance(msg, Response)
        assert msg.id == "cmd_1"
        assert msg.success is True
        assert msg.data == "Hello"

    def test_parse_error_response(self):
        raw = json.dumps({
            "id": "cmd_2",
            "success": False,
            "error": "ElementNotFoundError",
            "message": "not found",
        })
        msg = parse_message(raw)
        assert isinstance(msg, Response)
        assert msg.success is False
        assert msg.error == "ElementNotFoundError"
        assert msg.message == "not found"

    def test_parse_event(self):
        raw = json.dumps({"event": "tab_closed", "tabId": 42})
        msg = parse_message(raw)
        assert isinstance(msg, Event)
        assert msg.event == "tab_closed"
        assert msg.tab_id == 42

    def test_parse_invalid_json_raises(self):
        with pytest.raises(ValueError):
            parse_message("not json{{{")

    def test_parse_unknown_format_raises(self):
        with pytest.raises(ValueError):
            parse_message(json.dumps({"random": "data"}))
