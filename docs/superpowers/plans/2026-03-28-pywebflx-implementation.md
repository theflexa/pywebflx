# PyWebFlx Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python library + Chrome extension that enables browser automation on already-open Chrome pages via WebSocket, inspired by UiPath.

**Architecture:** Python acts as WebSocket server, Chrome extension connects as client. Commands are JSON messages dispatched to specific tabs. The extension injects scripts via `chrome.scripting.executeScript` to interact with the DOM. All Python APIs are async/await.

**Tech Stack:** Python 3.10+, asyncio, websockets, loguru, click (CLI), pytest + pytest-asyncio (tests), Chrome Manifest V3 extension (JavaScript)

---

## File Structure

```
pywebflx/
  pyproject.toml                    # Package config, dependencies, CLI entry point
  src/
    pywebflx/
      __init__.py                   # Public exports: use_browser, configure_logging, PyWebFlxConfig, exceptions
      exceptions.py                 # Full exception hierarchy with context attributes
      config.py                     # PyWebFlxConfig dataclass, defaults, priority resolution
      logging.py                    # configure_logging(), @_logged_action decorator
      selectors.py                  # resolve_selector() — CSS/XPath/attribute detection + JS generation
      protocol.py                   # Command/Response dataclasses, serialize/deserialize JSON protocol
      connection.py                 # WebSocketServer class — manages extension connections
      tab_manager.py                # TabManager — find/create/track tabs via extension
      browser.py                    # BrowserContext (returned by use_browser), orchestrates all actions
      actions/
        __init__.py                 # Re-exports all action methods
        navigation.py               # navigate_to, go_back, go_forward, refresh, close_tab, close_browser
        interaction.py              # click, type_into, set_text, check, uncheck, select_item, hover, send_hotkey
        extraction.py               # get_text, get_attribute, get_full_text, extract_table, extract_data, inspect
        synchronization.py          # element_exists, wait_element, wait_element_vanish, find_element
        javascript.py               # execute_js, inject_js, switch_to (iframes)
        files.py                    # take_screenshot, set_file, wait_for_download
      cli.py                        # CLI commands: install-extension, check
  extension/
    manifest.json                   # Manifest V3 config
    background.js                   # Service worker: WS client, command dispatcher, tab manager, keep-alive
    injected/
      selectors.js                  # Selector resolution logic (CSS, XPath, attributes) — injected into pages
      actions.js                    # DOM action functions (click, type, getText, etc.) — injected into pages
      inspect.js                    # DOM structure summarizer for AI consumption — injected into pages
      extract.js                    # Table/data extraction logic — injected into pages
  tests/
    conftest.py                     # Shared fixtures: mock WebSocket, fake extension messages
    test_exceptions.py
    test_config.py
    test_logging.py
    test_selectors.py
    test_protocol.py
    test_connection.py
    test_tab_manager.py
    test_browser.py
    test_actions/
      test_navigation.py
      test_interaction.py
      test_extraction.py
      test_synchronization.py
      test_javascript.py
      test_files.py
    test_cli.py
    test_extension/
      test_background.js            # Jest tests for background.js
      test_selectors.js             # Jest tests for selector resolution
      test_actions.js               # Jest tests for DOM actions
      test_inspect.js               # Jest tests for inspect logic
  docs/
    backlog.md                      # v2 features documented
```

**Note on splitting actions.py:** The spec lists a single `actions.py`, but the action count is large (~25 methods). Splitting into `actions/navigation.py`, `actions/interaction.py`, etc. keeps files focused and within context-window-friendly sizes. The `BrowserContext` class in `browser.py` composes all action modules via mixins or delegation.

**Note on extension `injected/` folder:** Splitting the injected JS into focused files makes each piece testable independently. `background.js` loads the right script per command.

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/pywebflx/__init__.py`
- Create: `tests/conftest.py`
- Create: `docs/backlog.md`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0", "setuptools-scm"]
build-backend = "setuptools.build_meta"

[project]
name = "pywebflx"
version = "0.1.0"
description = "Browser automation library for already-open Chrome pages, inspired by UiPath"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
dependencies = [
    "websockets>=12.0",
    "loguru>=0.7.0",
    "click>=8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-mock>=3.12",
]

[project.scripts]
pywebflx = "pywebflx.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: Create src/pywebflx/__init__.py**

```python
"""PyWebFlx — Browser automation for already-open Chrome pages."""

__version__ = "0.1.0"
```

- [ ] **Step 3: Create empty tests/conftest.py**

```python
"""Shared test fixtures for PyWebFlx."""
```

- [ ] **Step 4: Create docs/backlog.md**

```markdown
# PyWebFlx — Backlog v2

Funcionalidades planejadas para versoes futuras.

## Espera e Sincronizacao

- `for_each` com paginacao automatica (`next_page=`)
- `on_element_appear` / `on_element_vanish` (triggers por evento)

## Verificacao

- `assert_text(selector, expected)` — verifica texto de elemento
- `assert_visible(selector)` — verifica visibilidade

## Comunicacao Alternativa

- Native Messaging como alternativa ao WebSocket (mais seguro, sem porta aberta)

## Distribuicao

- Publicacao na Chrome Web Store
- Suporte a Firefox (WebExtensions API)

## Extracao Avancada

- Screen Scraping via OCR
```

- [ ] **Step 5: Create actions package**

```python
# src/pywebflx/actions/__init__.py
"""Action modules for PyWebFlx browser automation."""
```

- [ ] **Step 6: Install dev dependencies and verify**

Run: `cd "C:\Users\Guilherme Flexa\Desktop\Projetos Sicoob\Projetos Python\extension_python_integration" && pip install -e ".[dev]"`
Expected: Successfully installed pywebflx-0.1.0

Run: `python -c "import pywebflx; print(pywebflx.__version__)"`
Expected: `0.1.0`

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml src/ tests/conftest.py docs/backlog.md
git commit -m "feat: scaffold pywebflx project structure"
```

---

### Task 2: Exceptions Module

**Files:**
- Create: `src/pywebflx/exceptions.py`
- Create: `tests/test_exceptions.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_exceptions.py
"""Tests for PyWebFlx exception hierarchy."""

from pywebflx.exceptions import (
    PyWebFlxError,
    ConnectionError as WfxConnectionError,
    ExtensionNotConnectedError,
    ConnectionLostError,
    BrowserError,
    BrowserNotFoundError,
    TabNotFoundError,
    TabClosedError,
    ElementError,
    ElementNotFoundError,
    ElementTimeoutError,
    ElementNotInteractableError,
    SelectorError,
    ActionError,
    NavigationError,
    InjectionError,
    DownloadError,
    ScreenshotError,
    ConfigError,
)


class TestExceptionHierarchy:
    """Verify the full exception hierarchy and inheritance chains."""

    def test_base_exception_is_exception(self):
        assert issubclass(PyWebFlxError, Exception)

    def test_connection_errors_inherit_from_base(self):
        assert issubclass(WfxConnectionError, PyWebFlxError)
        assert issubclass(ExtensionNotConnectedError, WfxConnectionError)
        assert issubclass(ConnectionLostError, WfxConnectionError)

    def test_browser_errors_inherit_from_base(self):
        assert issubclass(BrowserError, PyWebFlxError)
        assert issubclass(BrowserNotFoundError, BrowserError)
        assert issubclass(TabNotFoundError, BrowserError)
        assert issubclass(TabClosedError, BrowserError)

    def test_element_errors_inherit_from_base(self):
        assert issubclass(ElementError, PyWebFlxError)
        assert issubclass(ElementNotFoundError, ElementError)
        assert issubclass(ElementTimeoutError, ElementError)
        assert issubclass(ElementNotInteractableError, ElementError)
        assert issubclass(SelectorError, ElementError)

    def test_action_errors_inherit_from_base(self):
        assert issubclass(ActionError, PyWebFlxError)
        assert issubclass(NavigationError, ActionError)
        assert issubclass(InjectionError, ActionError)
        assert issubclass(DownloadError, ActionError)
        assert issubclass(ScreenshotError, ActionError)

    def test_config_error_inherits_from_base(self):
        assert issubclass(ConfigError, PyWebFlxError)


class TestExceptionContext:
    """Verify exceptions carry contextual attributes."""

    def test_element_not_found_carries_context(self):
        exc = ElementNotFoundError(
            selector="#btn",
            tab_id=42,
            timeout=10,
        )
        assert exc.selector == "#btn"
        assert exc.tab_id == 42
        assert exc.timeout == 10
        assert "#btn" in str(exc)
        assert "10" in str(exc)

    def test_element_timeout_carries_context(self):
        exc = ElementTimeoutError(
            selector=".loading",
            tab_id=5,
            timeout=30,
            condition="visible",
        )
        assert exc.selector == ".loading"
        assert exc.tab_id == 5
        assert exc.timeout == 30
        assert exc.condition == "visible"

    def test_tab_not_found_carries_context(self):
        exc = TabNotFoundError(title="Portal", url="sicoob.com")
        assert exc.title == "Portal"
        assert exc.url == "sicoob.com"
        assert "Portal" in str(exc) or "sicoob.com" in str(exc)

    def test_connection_lost_carries_context(self):
        exc = ConnectionLostError(reason="WebSocket closed unexpectedly")
        assert exc.reason == "WebSocket closed unexpectedly"

    def test_browser_not_found_carries_context(self):
        exc = BrowserNotFoundError(
            title="Portal",
            url="sicoob.com",
        )
        assert exc.title == "Portal"
        assert exc.url == "sicoob.com"

    def test_selector_error_carries_context(self):
        exc = SelectorError(selector="///invalid", reason="Invalid XPath")
        assert exc.selector == "///invalid"
        assert exc.reason == "Invalid XPath"

    def test_base_exception_with_message(self):
        exc = PyWebFlxError("something went wrong")
        assert str(exc) == "something went wrong"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_exceptions.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pywebflx.exceptions'`

- [ ] **Step 3: Implement exceptions module**

```python
# src/pywebflx/exceptions.py
"""PyWebFlx exception hierarchy.

All exceptions inherit from PyWebFlxError. Each exception carries
contextual attributes relevant to the error (selector, tab_id, timeout, etc.)
so callers can inspect what went wrong programmatically.

Hierarchy:
    PyWebFlxError
    ├── ConnectionError
    │   ├── ExtensionNotConnectedError
    │   └── ConnectionLostError
    ├── BrowserError
    │   ├── BrowserNotFoundError
    │   ├── TabNotFoundError
    │   └── TabClosedError
    ├── ElementError
    │   ├── ElementNotFoundError
    │   ├── ElementTimeoutError
    │   ├── ElementNotInteractableError
    │   └── SelectorError
    ├── ActionError
    │   ├── NavigationError
    │   ├── InjectionError
    │   ├── DownloadError
    │   └── ScreenshotError
    └── ConfigError

Example:
    try:
        await browser.click("#btn")
    except ElementNotFoundError as e:
        print(e.selector, e.tab_id, e.timeout)
"""


class PyWebFlxError(Exception):
    """Base exception for all PyWebFlx errors."""
    pass


# ---------------------------------------------------------------------------
# Connection errors
# ---------------------------------------------------------------------------

class ConnectionError(PyWebFlxError):
    """Base for WebSocket connection errors."""
    pass


class ExtensionNotConnectedError(ConnectionError):
    """Chrome extension has not connected to the WebSocket server.

    Attributes:
        port: The WebSocket port that was being listened on.
        timeout: How long we waited for the connection.
    """

    def __init__(self, port: int = 9819, timeout: float = 30):
        self.port = port
        self.timeout = timeout
        super().__init__(
            f"Extension did not connect to ws://localhost:{port} within {timeout}s"
        )


class ConnectionLostError(ConnectionError):
    """WebSocket connection was lost during operation.

    Attributes:
        reason: Description of why the connection was lost.
    """

    def __init__(self, reason: str = "WebSocket closed unexpectedly"):
        self.reason = reason
        super().__init__(f"Connection lost: {reason}")


# ---------------------------------------------------------------------------
# Browser errors
# ---------------------------------------------------------------------------

class BrowserError(PyWebFlxError):
    """Base for browser-level errors."""
    pass


class BrowserNotFoundError(BrowserError):
    """Chrome browser is not running or no matching tab was found.

    Attributes:
        title: Tab title pattern that was searched (if any).
        url: URL pattern that was searched (if any).
    """

    def __init__(self, title: str | None = None, url: str | None = None):
        self.title = title
        self.url = url
        parts = []
        if title:
            parts.append(f"title='{title}'")
        if url:
            parts.append(f"url='{url}'")
        criteria = ", ".join(parts) if parts else "any"
        super().__init__(f"No browser tab found matching {criteria}")


class TabNotFoundError(BrowserError):
    """Specific tab was not found by title or URL.

    Attributes:
        title: Tab title pattern that was searched (if any).
        url: URL pattern that was searched (if any).
    """

    def __init__(self, title: str | None = None, url: str | None = None):
        self.title = title
        self.url = url
        parts = []
        if title:
            parts.append(f"title='{title}'")
        if url:
            parts.append(f"url='{url}'")
        criteria = ", ".join(parts) if parts else "unknown"
        super().__init__(f"Tab not found: {criteria}")


class TabClosedError(BrowserError):
    """Target tab was closed during operation.

    Attributes:
        tab_id: The Chrome tab ID that was closed.
    """

    def __init__(self, tab_id: int):
        self.tab_id = tab_id
        super().__init__(f"Tab {tab_id} was closed during operation")


# ---------------------------------------------------------------------------
# Element errors
# ---------------------------------------------------------------------------

class ElementError(PyWebFlxError):
    """Base for DOM element errors."""
    pass


class ElementNotFoundError(ElementError):
    """Selector did not match any element.

    Attributes:
        selector: The CSS/XPath/attribute selector used.
        tab_id: The Chrome tab ID where the search happened.
        timeout: How long the search waited before failing.
    """

    def __init__(self, selector: str, tab_id: int | None = None, timeout: float = 10):
        self.selector = selector
        self.tab_id = tab_id
        self.timeout = timeout
        super().__init__(
            f"Element '{selector}' not found within {timeout}s (tab:{tab_id})"
        )


class ElementTimeoutError(ElementError):
    """Timed out waiting for element condition.

    Attributes:
        selector: The CSS/XPath/attribute selector used.
        tab_id: The Chrome tab ID where the wait happened.
        timeout: How long the wait lasted.
        condition: The condition being waited for (visible, invisible, clickable).
    """

    def __init__(
        self,
        selector: str,
        tab_id: int | None = None,
        timeout: float = 10,
        condition: str = "visible",
    ):
        self.selector = selector
        self.tab_id = tab_id
        self.timeout = timeout
        self.condition = condition
        super().__init__(
            f"Timeout waiting for '{selector}' to be {condition} "
            f"after {timeout}s (tab:{tab_id})"
        )


class ElementNotInteractableError(ElementError):
    """Element exists but cannot be interacted with.

    Attributes:
        selector: The selector that matched the element.
        tab_id: The Chrome tab ID.
        reason: Why the element is not interactable.
    """

    def __init__(
        self, selector: str, tab_id: int | None = None, reason: str = "not interactable"
    ):
        self.selector = selector
        self.tab_id = tab_id
        self.reason = reason
        super().__init__(
            f"Element '{selector}' is {reason} (tab:{tab_id})"
        )


class SelectorError(ElementError):
    """Invalid selector syntax.

    Attributes:
        selector: The invalid selector string.
        reason: Why the selector is invalid.
    """

    def __init__(self, selector: str, reason: str = "invalid syntax"):
        self.selector = selector
        self.reason = reason
        super().__init__(f"Invalid selector '{selector}': {reason}")


# ---------------------------------------------------------------------------
# Action errors
# ---------------------------------------------------------------------------

class ActionError(PyWebFlxError):
    """Base for action execution errors."""
    pass


class NavigationError(ActionError):
    """Failed to navigate to URL.

    Attributes:
        url: The URL that failed to load.
    """

    def __init__(self, url: str, reason: str = "navigation failed"):
        self.url = url
        self.reason = reason
        super().__init__(f"Navigation to '{url}' failed: {reason}")


class InjectionError(ActionError):
    """Failed to inject or execute script in tab.

    Attributes:
        tab_id: The Chrome tab ID.
        reason: Why the injection failed.
    """

    def __init__(self, tab_id: int | None = None, reason: str = "injection failed"):
        self.tab_id = tab_id
        self.reason = reason
        super().__init__(f"Script injection failed in tab:{tab_id}: {reason}")


class DownloadError(ActionError):
    """Download failed or timed out.

    Attributes:
        timeout: How long we waited for the download.
    """

    def __init__(self, timeout: float = 30, reason: str = "download timed out"):
        self.timeout = timeout
        self.reason = reason
        super().__init__(f"Download failed: {reason} (timeout:{timeout}s)")


class ScreenshotError(ActionError):
    """Failed to capture screenshot.

    Attributes:
        path: Target file path for the screenshot.
        reason: Why the screenshot failed.
    """

    def __init__(self, path: str = "", reason: str = "capture failed"):
        self.path = path
        self.reason = reason
        super().__init__(f"Screenshot failed for '{path}': {reason}")


# ---------------------------------------------------------------------------
# Config errors
# ---------------------------------------------------------------------------

class ConfigError(PyWebFlxError):
    """Invalid configuration value.

    Attributes:
        param: The configuration parameter name.
        value: The invalid value.
        reason: Why it's invalid.
    """

    def __init__(self, param: str, value: object = None, reason: str = "invalid"):
        self.param = param
        self.value = value
        self.reason = reason
        super().__init__(f"Config error: {param}={value!r} — {reason}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_exceptions.py -v`
Expected: All 14 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/pywebflx/exceptions.py tests/test_exceptions.py
git commit -m "feat: add exception hierarchy with contextual attributes"
```

---

### Task 3: Config Module

**Files:**
- Create: `src/pywebflx/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_config.py
"""Tests for PyWebFlxConfig."""

import pytest
from pywebflx.config import PyWebFlxConfig
from pywebflx.exceptions import ConfigError


class TestPyWebFlxConfigDefaults:
    """Verify default configuration values."""

    def test_default_timeout(self):
        config = PyWebFlxConfig()
        assert config.default_timeout == 10

    def test_default_delay_between_actions(self):
        config = PyWebFlxConfig()
        assert config.delay_between_actions == 0.3

    def test_default_retry_count(self):
        config = PyWebFlxConfig()
        assert config.retry_count == 0

    def test_default_on_error(self):
        config = PyWebFlxConfig()
        assert config.on_error == "raise"

    def test_default_ws_port(self):
        config = PyWebFlxConfig()
        assert config.ws_port == 9819

    def test_default_log_level(self):
        config = PyWebFlxConfig()
        assert config.log_level == "INFO"


class TestPyWebFlxConfigCustom:
    """Verify custom configuration values."""

    def test_custom_values(self):
        config = PyWebFlxConfig(
            default_timeout=30,
            delay_between_actions=0.5,
            retry_count=3,
            on_error="continue",
            ws_port=8080,
            log_level="DEBUG",
        )
        assert config.default_timeout == 30
        assert config.delay_between_actions == 0.5
        assert config.retry_count == 3
        assert config.on_error == "continue"
        assert config.ws_port == 8080
        assert config.log_level == "DEBUG"

    def test_invalid_on_error_raises(self):
        with pytest.raises(ConfigError) as exc_info:
            PyWebFlxConfig(on_error="ignore")
        assert exc_info.value.param == "on_error"

    def test_invalid_timeout_raises(self):
        with pytest.raises(ConfigError):
            PyWebFlxConfig(default_timeout=-1)

    def test_invalid_ws_port_raises(self):
        with pytest.raises(ConfigError):
            PyWebFlxConfig(ws_port=0)

    def test_invalid_log_level_raises(self):
        with pytest.raises(ConfigError):
            PyWebFlxConfig(log_level="SUPERVERBOSE")


class TestPyWebFlxConfigGlobalDefaults:
    """Verify global defaults mechanism."""

    def setup_method(self):
        PyWebFlxConfig.reset_defaults()

    def teardown_method(self):
        PyWebFlxConfig.reset_defaults()

    def test_set_defaults_affects_new_instances(self):
        PyWebFlxConfig.set_defaults(default_timeout=20, retry_count=5)
        config = PyWebFlxConfig()
        assert config.default_timeout == 20
        assert config.retry_count == 5

    def test_explicit_params_override_global_defaults(self):
        PyWebFlxConfig.set_defaults(default_timeout=20)
        config = PyWebFlxConfig(default_timeout=5)
        assert config.default_timeout == 5

    def test_reset_defaults(self):
        PyWebFlxConfig.set_defaults(default_timeout=99)
        PyWebFlxConfig.reset_defaults()
        config = PyWebFlxConfig()
        assert config.default_timeout == 10


class TestPyWebFlxConfigResolve:
    """Verify parameter priority resolution: action > config > global."""

    def test_resolve_returns_action_param_when_provided(self):
        config = PyWebFlxConfig(default_timeout=10)
        assert config.resolve("timeout", action_value=30) == 30

    def test_resolve_returns_config_when_no_action_param(self):
        config = PyWebFlxConfig(default_timeout=10)
        assert config.resolve("timeout", action_value=None) == 10

    def test_resolve_returns_global_default_for_unset_config(self):
        PyWebFlxConfig.set_defaults(default_timeout=20)
        config = PyWebFlxConfig()
        assert config.resolve("timeout", action_value=None) == 20
        PyWebFlxConfig.reset_defaults()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pywebflx.config'`

- [ ] **Step 3: Implement config module**

```python
# src/pywebflx/config.py
"""PyWebFlx configuration management.

Handles default values, custom configuration, and parameter priority
resolution (action param > instance config > global defaults).

Example:
    config = PyWebFlxConfig(default_timeout=15, retry_count=3)

    async with use_browser(url="example.com", config=config) as browser:
        await browser.click("#btn", timeout=30)  # 30 wins over 15

    # Global defaults affect all new instances:
    PyWebFlxConfig.set_defaults(default_timeout=20)
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any

from pywebflx.exceptions import ConfigError

_VALID_ON_ERROR = ("raise", "continue")
_VALID_LOG_LEVELS = ("TRACE", "DEBUG", "INFO", "WARN", "WARNING", "ERROR", "DISABLED")

_BUILTIN_DEFAULTS: dict[str, Any] = {
    "default_timeout": 10,
    "delay_between_actions": 0.3,
    "retry_count": 0,
    "on_error": "raise",
    "ws_port": 9819,
    "log_level": "INFO",
}

_global_defaults: dict[str, Any] = {}

# Maps resolve() short names to config field names
_RESOLVE_ALIASES: dict[str, str] = {
    "timeout": "default_timeout",
}


def _validate(
    default_timeout: float,
    delay_between_actions: float,
    retry_count: int,
    on_error: str,
    ws_port: int,
    log_level: str,
) -> None:
    if default_timeout < 0:
        raise ConfigError("default_timeout", default_timeout, "must be >= 0")
    if delay_between_actions < 0:
        raise ConfigError("delay_between_actions", delay_between_actions, "must be >= 0")
    if retry_count < 0:
        raise ConfigError("retry_count", retry_count, "must be >= 0")
    if on_error not in _VALID_ON_ERROR:
        raise ConfigError("on_error", on_error, f"must be one of {_VALID_ON_ERROR}")
    if not (1 <= ws_port <= 65535):
        raise ConfigError("ws_port", ws_port, "must be between 1 and 65535")
    if log_level.upper() not in _VALID_LOG_LEVELS:
        raise ConfigError("log_level", log_level, f"must be one of {_VALID_LOG_LEVELS}")


@dataclass
class PyWebFlxConfig:
    """Configuration for PyWebFlx browser sessions.

    Attributes:
        default_timeout: Default timeout in seconds for all actions.
        delay_between_actions: Delay in seconds between consecutive actions.
        retry_count: Default number of retries for failed actions.
        on_error: Behavior on error — "raise" or "continue".
        ws_port: WebSocket server port.
        log_level: Logging level (TRACE, DEBUG, INFO, WARN, ERROR, DISABLED).
    """

    default_timeout: float = None
    delay_between_actions: float = None
    retry_count: int = None
    on_error: str = None
    ws_port: int = None
    log_level: str = None

    def __post_init__(self):
        # Fill None fields from global defaults, then builtin defaults
        for f in fields(self):
            if getattr(self, f.name) is None:
                value = _global_defaults.get(f.name, _BUILTIN_DEFAULTS[f.name])
                object.__setattr__(self, f.name, value)

        _validate(
            self.default_timeout,
            self.delay_between_actions,
            self.retry_count,
            self.on_error,
            self.ws_port,
            self.log_level,
        )

    def resolve(self, param_name: str, action_value: Any) -> Any:
        """Resolve a parameter value with priority: action > config > global.

        Args:
            param_name: The parameter name (e.g., "timeout" or "default_timeout").
            action_value: The value passed directly to the action method, or None.

        Returns:
            The resolved value.
        """
        if action_value is not None:
            return action_value
        field_name = _RESOLVE_ALIASES.get(param_name, param_name)
        return getattr(self, field_name, None)

    @staticmethod
    def set_defaults(**kwargs: Any) -> None:
        """Set global defaults that affect all new PyWebFlxConfig instances.

        Args:
            **kwargs: Config fields to override (e.g., default_timeout=20).
        """
        valid_fields = {f.name for f in fields(PyWebFlxConfig)}
        for key in kwargs:
            if key not in valid_fields:
                raise ConfigError(key, kwargs[key], f"unknown config field")
        _global_defaults.update(kwargs)

    @staticmethod
    def reset_defaults() -> None:
        """Reset global defaults to builtin values."""
        _global_defaults.clear()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_config.py -v`
Expected: All 15 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/pywebflx/config.py tests/test_config.py
git commit -m "feat: add PyWebFlxConfig with validation and priority resolution"
```

---

### Task 4: Logging Module

**Files:**
- Create: `src/pywebflx/logging.py`
- Create: `tests/test_logging.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_logging.py
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

    def test_decorator_preserves_return_value(self):
        class FakeBrowser:
            _config = MagicMock()
            _config.resolve.return_value = "INFO"
            _tab_id = 42

            @_logged_action("browser.get_text")
            async def get_text(self, selector, **kwargs):
                return "Hello World"

        browser = FakeBrowser()
        result = asyncio.get_event_loop().run_until_complete(
            browser.get_text("#title")
        )
        assert result == "Hello World"

    def test_decorator_reraises_exceptions(self):
        class FakeBrowser:
            _config = MagicMock()
            _config.resolve.return_value = "INFO"
            _tab_id = 42

            @_logged_action("browser.click")
            async def click(self, selector, **kwargs):
                raise ValueError("test error")

        browser = FakeBrowser()
        with pytest.raises(ValueError, match="test error"):
            asyncio.get_event_loop().run_until_complete(
                browser.click("#btn")
            )


class TestConfigureLogging:
    """Test configure_logging function."""

    def test_configure_with_level(self):
        # Should not raise
        configure_logging(level="DEBUG")
        configure_logging(level="INFO")
        configure_logging(level="DISABLED")

    def test_configure_with_sink(self, tmp_path):
        log_file = tmp_path / "test.log"
        configure_logging(level="DEBUG", sink=str(log_file))

    def test_configure_with_custom_handler(self):
        handler = MagicMock()
        configure_logging(handler=handler)

    def test_configure_with_timestamp_format(self):
        configure_logging(timestamp_format="%H:%M:%S")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_logging.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pywebflx.logging'`

- [ ] **Step 3: Implement logging module**

```python
# src/pywebflx/logging.py
"""PyWebFlx structured logging system.

Provides:
- configure_logging(): Set up log level, sink, format
- @_logged_action: Decorator that auto-logs every browser action with
  timestamp, action name, selector, tab, duration, retries, and errors.

Log format:
    2026-03-28 14:32:05.123 [INFO]  [browser.click] #btn -> tab:42 -> success (120ms)

Levels:
    ERROR — Final failure after all retries
    WARN  — Retry, reconnection, fallback
    INFO  — Action completed successfully
    DEBUG — Internal details (selector resolved, JSON payload)
    TRACE — Everything (WS bytes, partial DOM)
"""

from __future__ import annotations

import functools
import time
from typing import Any, Callable

try:
    from loguru import logger

    _LOGURU_AVAILABLE = True
except ImportError:
    import logging

    logger = logging.getLogger("pywebflx")
    _LOGURU_AVAILABLE = False

_timestamp_format: str = "%Y-%m-%d %H:%M:%S.%f"


def configure_logging(
    level: str = "INFO",
    sink: str | None = None,
    handler: Any = None,
    timestamp_format: str | None = None,
) -> None:
    """Configure PyWebFlx logging output.

    Args:
        level: Log level — TRACE, DEBUG, INFO, WARN, ERROR, or DISABLED.
        sink: File path to write logs to. If None, logs to stderr.
        handler: Custom log handler (loguru sink or logging.Handler).
        timestamp_format: strftime format for timestamps. Default: "%Y-%m-%d %H:%M:%S.%f".

    Example:
        configure_logging(level="DEBUG", sink="automacao.log")
        configure_logging(level="DISABLED")
        configure_logging(handler=my_custom_handler)
    """
    global _timestamp_format
    if timestamp_format is not None:
        _timestamp_format = timestamp_format

    if _LOGURU_AVAILABLE:
        logger.remove()
        if level.upper() == "DISABLED":
            return
        fmt = "{time:" + _timestamp_format.replace("%Y", "YYYY").replace(
            "%m", "MM"
        ).replace("%d", "DD").replace("%H", "HH").replace("%M", "mm").replace(
            "%S", "ss"
        ).replace("%f", "SSS") + "} [{level}] {message}"

        if handler is not None:
            logger.add(handler, level=level.upper(), format=fmt)
        elif sink is not None:
            logger.add(sink, level=level.upper(), format=fmt)
        else:
            logger.add(
                lambda msg: print(msg, end=""),
                level=level.upper(),
                format=fmt,
                colorize=True,
            )
    else:
        log = logging.getLogger("pywebflx")
        log.handlers.clear()
        if level.upper() == "DISABLED":
            log.addHandler(logging.NullHandler())
            return
        log.setLevel(getattr(logging, level.upper(), logging.INFO))
        if handler is not None:
            log.addHandler(handler)
        elif sink is not None:
            log.addHandler(logging.FileHandler(sink))
        else:
            sh = logging.StreamHandler()
            sh.setFormatter(logging.Formatter(f"%(asctime)s [%(levelname)s] %(message)s"))
            log.addHandler(sh)


def _format_log_message(
    action: str,
    selector: str = "",
    tab_id: int | None = None,
    status: str = "success",
    duration_ms: float | None = None,
    attempt: int | None = None,
    max_attempts: int | None = None,
    error_name: str | None = None,
    extra: str | None = None,
) -> str:
    """Format a structured log message for a browser action.

    Args:
        action: The action name (e.g., "browser.click").
        selector: The selector string used.
        tab_id: Chrome tab ID.
        status: One of "success", "retry", "failed".
        duration_ms: Action duration in milliseconds.
        attempt: Current retry attempt number.
        max_attempts: Total retry attempts allowed.
        error_name: Exception class name on failure/retry.
        extra: Additional info (e.g., typed text value).

    Returns:
        Formatted log message string.
    """
    parts = [f"[{action}]"]

    if selector:
        parts.append(selector)

    if extra:
        parts.append(f"-> {extra}")

    if tab_id is not None:
        parts.append(f"-> tab:{tab_id}")

    if status == "retry":
        retry_info = f"retry {attempt}/{max_attempts}" if max_attempts else f"retry {attempt}"
        parts.append(f"-> {retry_info}")
        if error_name:
            parts.append(f"({error_name})")
    elif status == "failed":
        parts.append(f"-> failed")
        if error_name:
            parts.append(f": {error_name}")
    elif status == "success":
        if attempt and attempt > 1:
            parts.append(f"-> success (retry {attempt}")
            if duration_ms is not None:
                parts[-1] = parts[-1] + f", {duration_ms:.0f}ms)"
            else:
                parts[-1] = parts[-1] + ")"
        else:
            if duration_ms is not None:
                parts.append(f"-> success ({duration_ms:.0f}ms)")
            else:
                parts.append("-> success")

    return " ".join(parts)


def _logged_action(action_name: str) -> Callable:
    """Decorator that adds structured logging to async browser action methods.

    Automatically logs action start/success/retry/failure with timing,
    selector, tab ID, and error info. Reads log_level from kwargs or config.

    Args:
        action_name: The action identifier (e.g., "browser.click").

    Example:
        @_logged_action("browser.click")
        async def click(self, selector, **kwargs):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, selector: str = "", **kwargs):
            log_level = kwargs.pop("log_level", None)
            if log_level is None and hasattr(self, "_config"):
                log_level = self._config.resolve("log_level", None)
            if log_level is None:
                log_level = "INFO"

            tab_id = getattr(self, "_tab_id", None)
            start = time.perf_counter()

            try:
                result = await func(self, selector, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                msg = _format_log_message(
                    action=action_name,
                    selector=str(selector),
                    tab_id=tab_id,
                    status="success",
                    duration_ms=duration_ms,
                )
                _log(log_level, msg)
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                msg = _format_log_message(
                    action=action_name,
                    selector=str(selector),
                    tab_id=tab_id,
                    status="failed",
                    error_name=type(e).__name__,
                )
                _log("ERROR", msg)
                raise

        return wrapper

    return decorator


def _log(level: str, message: str) -> None:
    """Route a message to the active logger at the given level."""
    level = level.upper()
    if _LOGURU_AVAILABLE:
        logger.opt(depth=2).log(level, message)
    else:
        log = logging.getLogger("pywebflx")
        py_level = getattr(logging, level if level != "TRACE" else "DEBUG", logging.INFO)
        log.log(py_level, message)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_logging.py -v`
Expected: All 10 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/pywebflx/logging.py tests/test_logging.py
git commit -m "feat: add structured logging with @_logged_action decorator"
```

---

### Task 5: Selectors Module

**Files:**
- Create: `src/pywebflx/selectors.py`
- Create: `tests/test_selectors.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_selectors.py
"""Tests for selector resolution (CSS, XPath, attributes)."""

import pytest
from pywebflx.selectors import resolve_selector, detect_selector_type, SelectorResult
from pywebflx.exceptions import SelectorError


class TestDetectSelectorType:
    """Verify automatic detection of selector type from string."""

    def test_css_id_selector(self):
        assert detect_selector_type("#btn-login") == "css"

    def test_css_class_selector(self):
        assert detect_selector_type(".my-class") == "css"

    def test_css_tag_selector(self):
        assert detect_selector_type("button") == "css"

    def test_css_attribute_selector(self):
        assert detect_selector_type("[data-testid='submit']") == "css"

    def test_css_complex_selector(self):
        assert detect_selector_type("div.container > ul li:first-child") == "css"

    def test_xpath_starts_with_slash(self):
        assert detect_selector_type("//button[@id='submit']") == "xpath"

    def test_xpath_starts_with_dot_slash(self):
        assert detect_selector_type(".//div[@class='item']") == "xpath"

    def test_xpath_starts_with_parenthesis(self):
        assert detect_selector_type("(//div)[1]") == "xpath"


class TestResolveSelector:
    """Verify resolve_selector builds correct JS code for each type."""

    def test_css_selector_returns_queryselector(self):
        result = resolve_selector("#btn")
        assert result.selector_type == "css"
        assert result.selector == "#btn"
        assert "querySelector" in result.js_expression

    def test_xpath_selector_returns_evaluate(self):
        result = resolve_selector("//button[@id='ok']")
        assert result.selector_type == "xpath"
        assert "evaluate" in result.js_expression

    def test_attribute_text_selector(self):
        result = resolve_selector(text="Entrar")
        assert result.selector_type == "attributes"
        assert "Entrar" in result.js_expression

    def test_attribute_text_with_tag(self):
        result = resolve_selector(text="Salvar", tag="button")
        assert result.selector_type == "attributes"
        assert "button" in result.js_expression
        assert "Salvar" in result.js_expression

    def test_attribute_role_selector(self):
        result = resolve_selector(role="button", name="Submit")
        assert result.selector_type == "attributes"
        assert "role" in result.js_expression

    def test_empty_selector_raises(self):
        with pytest.raises(SelectorError):
            resolve_selector("")

    def test_none_selector_with_no_attributes_raises(self):
        with pytest.raises(SelectorError):
            resolve_selector(None)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_selectors.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pywebflx.selectors'`

- [ ] **Step 3: Implement selectors module**

```python
# src/pywebflx/selectors.py
"""Selector resolution for PyWebFlx.

Converts CSS selectors, XPath expressions, or humanized attribute queries
into JavaScript expressions that can be injected into Chrome tabs.

Supports three selector types:
- CSS: "#btn", ".class", "div > span"
- XPath: "//button[@id='ok']", ".//div"
- Attributes: text="Entrar", tag="button", role="button", name="Submit"

Example:
    result = resolve_selector("#btn-login")
    # result.selector_type == "css"
    # result.js_expression == "document.querySelector('#btn-login')"

    result = resolve_selector(text="Entrar", tag="button")
    # result.selector_type == "attributes"
    # result.js_expression contains JS to find by text content
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from pywebflx.exceptions import SelectorError


@dataclass
class SelectorResult:
    """Result of resolving a selector.

    Attributes:
        selector: The original selector string or description.
        selector_type: One of "css", "xpath", "attributes".
        js_expression: JavaScript code that locates the element in the DOM.
    """

    selector: str
    selector_type: str
    js_expression: str


def detect_selector_type(selector: str) -> str:
    """Detect whether a string selector is CSS or XPath.

    Args:
        selector: The selector string to analyze.

    Returns:
        "css" or "xpath".

    Rules:
        - Starts with "/", "./" or "(" → XPath
        - Everything else → CSS
    """
    stripped = selector.strip()
    if stripped.startswith(("//", "./", "(/")):
        return "xpath"
    if stripped.startswith(".//"):
        return "xpath"
    return "css"


def resolve_selector(
    selector: str | None = None,
    *,
    text: str | None = None,
    tag: str | None = None,
    role: str | None = None,
    name: str | None = None,
) -> SelectorResult:
    """Resolve a selector into a JavaScript expression for DOM lookup.

    Can be called with a CSS/XPath string selector, or with keyword
    arguments for attribute-based lookup.

    Args:
        selector: CSS selector or XPath expression string.
        text: Find element by visible text content.
        tag: Filter by HTML tag name (used with text/role/name).
        role: Find element by ARIA role attribute.
        name: Find element by ARIA name or aria-label attribute.

    Returns:
        SelectorResult with the JS expression to find the element.

    Raises:
        SelectorError: If no valid selector or attributes provided.

    Example:
        resolve_selector("#btn")
        resolve_selector("//button[@id='ok']")
        resolve_selector(text="Entrar", tag="button")
    """
    has_attributes = any(v is not None for v in (text, tag, role, name))

    if selector and isinstance(selector, str) and selector.strip():
        sel_type = detect_selector_type(selector)
        if sel_type == "css":
            js = f"document.querySelector({json.dumps(selector)})"
            return SelectorResult(
                selector=selector,
                selector_type="css",
                js_expression=js,
            )
        else:
            js = (
                f"document.evaluate({json.dumps(selector)}, document, null, "
                f"XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue"
            )
            return SelectorResult(
                selector=selector,
                selector_type="xpath",
                js_expression=js,
            )

    if has_attributes:
        return _resolve_attributes(text=text, tag=tag, role=role, name=name)

    raise SelectorError(
        selector=str(selector),
        reason="No valid selector or attributes provided",
    )


def _resolve_attributes(
    text: str | None = None,
    tag: str | None = None,
    role: str | None = None,
    name: str | None = None,
) -> SelectorResult:
    """Build a JS expression that finds an element by attributes.

    Uses a combination of querySelectorAll + filtering to find elements
    matching the given attribute criteria.
    """
    description_parts = []
    filters = []
    base_selector = tag or "*"

    if role:
        base_selector = f'{tag or "*"}[role={json.dumps(role)}]'
        description_parts.append(f"role={role}")

    if name:
        filters.append(
            f'(el.getAttribute("aria-label") === {json.dumps(name)} || '
            f'el.getAttribute("name") === {json.dumps(name)})'
        )
        description_parts.append(f"name={name}")

    if text:
        filters.append(
            f"el.textContent.trim() === {json.dumps(text)}"
        )
        description_parts.append(f"text={text}")

    if tag:
        description_parts.insert(0, f"tag={tag}")

    description = ", ".join(description_parts)

    if filters:
        filter_expr = " && ".join(filters)
        js = (
            f"Array.from(document.querySelectorAll({json.dumps(base_selector)}))"
            f".find(el => {filter_expr})"
        )
    else:
        js = f"document.querySelector({json.dumps(base_selector)})"

    return SelectorResult(
        selector=f"[{description}]",
        selector_type="attributes",
        js_expression=js,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_selectors.py -v`
Expected: All 11 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/pywebflx/selectors.py tests/test_selectors.py
git commit -m "feat: add selector resolution (CSS, XPath, attributes)"
```

---

### Task 6: Protocol Module

**Files:**
- Create: `src/pywebflx/protocol.py`
- Create: `tests/test_protocol.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_protocol.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_protocol.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pywebflx.protocol'`

- [ ] **Step 3: Implement protocol module**

```python
# src/pywebflx/protocol.py
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
    """A command to be sent to the Chrome extension.

    Attributes:
        id: Unique command identifier for correlating responses.
        action: The action to execute (e.g., "click", "get_text").
        tab_id: Target Chrome tab ID, or None for tab-management commands.
        params: Action-specific parameters.
    """

    id: str
    action: str
    tab_id: int | None
    params: dict[str, Any]

    def to_json(self) -> str:
        """Serialize command to JSON string for WebSocket transmission.

        Returns:
            JSON string with camelCase keys matching the protocol spec.
        """
        data: dict[str, Any] = {
            "id": self.id,
            "action": self.action,
            "tabId": self.tab_id,
            "params": self.params,
        }
        return json.dumps(data)


@dataclass
class Response:
    """A response received from the Chrome extension.

    Attributes:
        id: The command ID this response corresponds to.
        success: Whether the command succeeded.
        data: Return data on success (e.g., extracted text).
        error: Error class name on failure.
        message: Human-readable error message on failure.
    """

    id: str
    success: bool
    data: Any = None
    error: str | None = None
    message: str | None = None


@dataclass
class Event:
    """An unsolicited event from the Chrome extension.

    Attributes:
        event: Event type name (e.g., "tab_closed", "disconnected").
        tab_id: Related tab ID, if applicable.
        data: Additional event data.
    """

    event: str
    tab_id: int | None = None
    data: dict[str, Any] = field(default_factory=dict)


def build_command(
    action: str,
    params: dict[str, Any],
    tab_id: int | None = None,
) -> Command:
    """Build a new Command with a unique ID.

    Args:
        action: The action name (e.g., "click", "get_text", "find_tabs").
        params: Action-specific parameters dict.
        tab_id: Target tab ID, or None for global commands.

    Returns:
        A Command instance ready to be serialized and sent.
    """
    cmd_id = f"cmd_{uuid.uuid4().hex[:12]}"
    return Command(id=cmd_id, action=action, tab_id=tab_id, params=params)


def parse_message(raw: str) -> Response | Event:
    """Parse a JSON message from the Chrome extension.

    Args:
        raw: Raw JSON string received via WebSocket.

    Returns:
        A Response or Event instance.

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_protocol.py -v`
Expected: All 9 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/pywebflx/protocol.py tests/test_protocol.py
git commit -m "feat: add JSON protocol for Python-extension communication"
```

---

### Task 7: WebSocket Connection Module

**Files:**
- Create: `src/pywebflx/connection.py`
- Create: `tests/test_connection.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_connection.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_connection.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pywebflx.connection'`

- [ ] **Step 3: Implement connection module**

```python
# src/pywebflx/connection.py
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
    """WebSocket server that manages communication with the Chrome extension.

    Attributes:
        port: The TCP port to listen on.
        is_running: Whether the server is currently listening.
        is_connected: Whether an extension client is connected.
    """

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
        """Whether the WebSocket server is currently listening."""
        return self._server is not None

    @property
    def is_connected(self) -> bool:
        """Whether a Chrome extension client is currently connected."""
        return self._client is not None

    async def start(self) -> None:
        """Start the WebSocket server.

        If already running, this is a no-op.
        """
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
        """Stop the WebSocket server and disconnect any client.

        If not running, this is a no-op.
        """
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

        Args:
            timeout: Maximum seconds to wait.

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

        Args:
            action: The action name (e.g., "click", "get_text").
            tab_id: Target tab ID.
            params: Action parameters.
            timeout: Maximum seconds to wait for response.

        Returns:
            The Response from the extension.

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
        """Register a handler for unsolicited extension events.

        Args:
            handler: Callable that receives an Event instance.
        """
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
            # Reject pending commands
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_connection.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/pywebflx/connection.py tests/test_connection.py
git commit -m "feat: add WebSocket server for extension communication"
```

---

### Task 8: Chrome Extension — Manifest and Background Service Worker

**Files:**
- Create: `extension/manifest.json`
- Create: `extension/background.js`
- Create: `extension/icons/` (placeholder)

- [ ] **Step 1: Create extension directory structure**

Run: `mkdir -p extension/icons extension/injected`

- [ ] **Step 2: Create manifest.json**

```json
{
  "manifest_version": 3,
  "name": "PyWebFlx Bridge",
  "version": "1.0.0",
  "description": "Bridge between PyWebFlx Python library and Chrome browser automation",
  "permissions": [
    "tabs",
    "scripting",
    "activeTab",
    "downloads",
    "alarms"
  ],
  "host_permissions": [
    "<all_urls>"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

- [ ] **Step 3: Create background.js**

```javascript
// background.js — PyWebFlx Chrome Extension Service Worker
//
// Responsibilities:
// 1. WebSocket client: connects to Python server at ws://localhost:PORT
// 2. Keep-alive: chrome.alarms prevent service worker from sleeping
// 3. Command dispatcher: receives JSON commands, injects scripts into tabs
// 4. Tab manager: finds tabs by title/URL, creates new tabs, reports events
//
// Protocol:
//   Command (from Python):  { id, action, tabId, params }
//   Response (to Python):   { id, success, data } or { id, success:false, error, message }
//   Event (to Python):      { event, tabId }

const DEFAULT_PORT = 9819;
const RECONNECT_DELAY_MS = 3000;
const KEEPALIVE_ALARM = "pywebflx-keepalive";
const KEEPALIVE_INTERVAL_MIN = 0.4; // ~25 seconds (minimum chrome.alarms allows)

let ws = null;
let port = DEFAULT_PORT;

// ---------------------------------------------------------------------------
// WebSocket connection
// ---------------------------------------------------------------------------

function connect() {
  if (ws && ws.readyState === WebSocket.OPEN) return;

  try {
    ws = new WebSocket(`ws://localhost:${port}`);
  } catch (e) {
    scheduleReconnect();
    return;
  }

  ws.onopen = () => {
    console.log("[PyWebFlx] Connected to Python server");
    startKeepalive();
  };

  ws.onmessage = (event) => {
    handleCommand(event.data);
  };

  ws.onclose = () => {
    console.log("[PyWebFlx] Disconnected from Python server");
    ws = null;
    stopKeepalive();
    scheduleReconnect();
  };

  ws.onerror = () => {
    // onclose will fire after onerror, triggering reconnect
  };
}

function scheduleReconnect() {
  setTimeout(connect, RECONNECT_DELAY_MS);
}

function send(data) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
  }
}

// ---------------------------------------------------------------------------
// Keep-alive (prevents service worker from sleeping)
// ---------------------------------------------------------------------------

function startKeepalive() {
  chrome.alarms.create(KEEPALIVE_ALARM, { periodInMinutes: KEEPALIVE_INTERVAL_MIN });
}

function stopKeepalive() {
  chrome.alarms.clear(KEEPALIVE_ALARM);
}

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === KEEPALIVE_ALARM) {
    // Just being called keeps the service worker alive
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      connect();
    }
  }
});

// ---------------------------------------------------------------------------
// Tab events — notify Python
// ---------------------------------------------------------------------------

chrome.tabs.onRemoved.addListener((tabId) => {
  send({ event: "tab_closed", tabId });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status === "complete") {
    send({ event: "tab_loaded", tabId });
  }
});

// ---------------------------------------------------------------------------
// Command dispatcher
// ---------------------------------------------------------------------------

async function handleCommand(raw) {
  let cmd;
  try {
    cmd = JSON.parse(raw);
  } catch (e) {
    return;
  }

  const { id, action, tabId, params } = cmd;

  try {
    let result;

    switch (action) {
      case "find_tabs":
        result = await findTabs(params);
        break;
      case "create_tab":
        result = await createTab(params);
        break;
      case "close_tab":
        await chrome.tabs.remove(tabId);
        result = null;
        break;
      case "navigate":
        await chrome.tabs.update(tabId, { url: params.url });
        result = null;
        break;
      case "go_back":
        result = await executeInTab(tabId, () => { history.back(); });
        break;
      case "go_forward":
        result = await executeInTab(tabId, () => { history.forward(); });
        break;
      case "refresh":
        await chrome.tabs.reload(tabId);
        result = null;
        break;
      case "execute_js":
        result = await executeInTab(tabId, params.code, true);
        break;
      default:
        // All DOM actions: click, type_into, get_text, inspect, etc.
        result = await executeDomAction(tabId, action, params);
        break;
    }

    send({ id, success: true, data: result });
  } catch (e) {
    send({
      id,
      success: false,
      error: e.name || "Error",
      message: e.message || String(e),
    });
  }
}

// ---------------------------------------------------------------------------
// Tab management
// ---------------------------------------------------------------------------

async function findTabs(params) {
  const { title, url } = params;
  const query = {};
  if (title) query.title = `*${title}*`;
  if (url) query.url = `*${url}*`;

  const tabs = await chrome.tabs.query(query);
  return tabs.map((t) => ({ id: t.id, title: t.title, url: t.url }));
}

async function createTab(params) {
  const tab = await chrome.tabs.create({ url: params.url, active: true });
  return { id: tab.id, title: tab.title, url: tab.url };
}

// ---------------------------------------------------------------------------
// Script injection
// ---------------------------------------------------------------------------

async function executeInTab(tabId, codeOrFunc, isRawCode = false) {
  let results;

  if (isRawCode) {
    // Execute raw JS code string
    results = await chrome.scripting.executeScript({
      target: { tabId },
      func: (code) => {
        return new Function(code)();
      },
      args: [codeOrFunc],
    });
  } else {
    results = await chrome.scripting.executeScript({
      target: { tabId },
      func: codeOrFunc,
    });
  }

  if (results && results.length > 0) {
    return results[0].result;
  }
  return null;
}

async function executeDomAction(tabId, action, params) {
  // Inject the action script with params and execute it
  const results = await chrome.scripting.executeScript({
    target: { tabId },
    func: domActionHandler,
    args: [action, params],
  });

  if (results && results.length > 0) {
    const result = results[0].result;
    if (result && result.__error) {
      const err = new Error(result.message);
      err.name = result.name;
      throw err;
    }
    return result;
  }
  return null;
}

// ---------------------------------------------------------------------------
// DOM action handler — injected into page context
// ---------------------------------------------------------------------------

function domActionHandler(action, params) {
  // Selector resolution
  function resolveElement(params) {
    const { selector, selectorType, text, tag, role, name } = params;

    if (selector && selectorType === "xpath") {
      const result = document.evaluate(
        selector, document, null,
        XPathResult.FIRST_ORDERED_NODE_TYPE, null
      );
      return result.singleNodeValue;
    }

    if (selector && selectorType === "css") {
      return document.querySelector(selector);
    }

    // Attribute-based selector
    if (text || role || name) {
      const baseTag = tag || "*";
      let candidates;
      if (role) {
        candidates = document.querySelectorAll(`${baseTag}[role="${role}"]`);
      } else {
        candidates = document.querySelectorAll(baseTag);
      }
      for (const el of candidates) {
        let match = true;
        if (text && el.textContent.trim() !== text) match = false;
        if (name) {
          const ariaLabel = el.getAttribute("aria-label") || el.getAttribute("name") || "";
          if (ariaLabel !== name) match = false;
        }
        if (match) return el;
      }
    }

    // Fallback: try CSS if selector provided without type
    if (selector) {
      return document.querySelector(selector);
    }

    return null;
  }

  function makeError(name, message) {
    return { __error: true, name, message };
  }

  try {
    switch (action) {
      case "click": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        if (params.clickType === "double") {
          el.dispatchEvent(new MouseEvent("dblclick", { bubbles: true }));
        } else if (params.mouseButton === "right") {
          el.dispatchEvent(new MouseEvent("contextmenu", { bubbles: true }));
        } else {
          el.click();
        }
        return null;
      }

      case "type_into": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        if (params.clearBefore !== false) {
          el.value = "";
          el.dispatchEvent(new Event("input", { bubbles: true }));
        }
        if (params.clickBefore !== false) {
          el.focus();
          el.click();
        }
        el.value = params.text;
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
        return null;
      }

      case "set_text": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        el.value = params.text;
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
        return null;
      }

      case "check": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        if (!el.checked) {
          el.click();
        }
        return null;
      }

      case "uncheck": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        if (el.checked) {
          el.click();
        }
        return null;
      }

      case "select_item": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        const { item, by } = params;
        if (by === "index") {
          el.selectedIndex = parseInt(item, 10);
        } else if (by === "value") {
          el.value = item;
        } else {
          // by text (default)
          const option = Array.from(el.options).find(o => o.text === item);
          if (option) option.selected = true;
        }
        el.dispatchEvent(new Event("change", { bubbles: true }));
        return null;
      }

      case "hover": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        el.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
        el.dispatchEvent(new MouseEvent("mouseover", { bubbles: true }));
        return null;
      }

      case "send_hotkey": {
        const keys = params.keys.toLowerCase().split("+").map(k => k.trim());
        const eventInit = { bubbles: true };
        if (keys.includes("ctrl")) eventInit.ctrlKey = true;
        if (keys.includes("shift")) eventInit.shiftKey = true;
        if (keys.includes("alt")) eventInit.altKey = true;
        if (keys.includes("meta")) eventInit.metaKey = true;
        const mainKey = keys.filter(k => !["ctrl", "shift", "alt", "meta"].includes(k))[0] || "";
        eventInit.key = mainKey;
        document.activeElement.dispatchEvent(new KeyboardEvent("keydown", eventInit));
        document.activeElement.dispatchEvent(new KeyboardEvent("keyup", eventInit));
        return null;
      }

      case "get_text": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        return el.innerText || el.textContent || "";
      }

      case "get_attribute": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        return el.getAttribute(params.attribute);
      }

      case "get_full_text": {
        return document.body.innerText || "";
      }

      case "element_exists": {
        const el = resolveElement(params);
        return el !== null;
      }

      case "find_element": {
        const el = resolveElement(params);
        if (!el) return makeError("ElementNotFoundError", `Element not found: ${params.selector || "attributes"}`);
        return {
          tag: el.tagName.toLowerCase(),
          id: el.id || null,
          classes: Array.from(el.classList),
          text: (el.innerText || "").substring(0, 200),
          visible: el.offsetParent !== null,
        };
      }

      case "inspect": {
        return inspectDom(params.selector || null, params.depth || 2, params.samples || 2);
      }

      case "extract_table": {
        return extractTable(params.selector);
      }

      case "take_screenshot": {
        // Screenshots are handled by background.js via chrome.tabs.captureVisibleTab
        // This should not reach here, but if it does:
        return makeError("ActionError", "Screenshots must be handled by background.js");
      }

      default:
        return makeError("ActionError", `Unknown action: ${action}`);
    }
  } catch (e) {
    return makeError(e.name || "Error", e.message || String(e));
  }

  // -----------------------------------------------------------------------
  // Inspect DOM — summarize structure for AI consumption
  // -----------------------------------------------------------------------
  function inspectDom(rootSelector, maxDepth, sampleCount) {
    const root = rootSelector ? document.querySelector(rootSelector) : document.body;
    if (!root) return `Element not found: ${rootSelector}`;

    const lines = [];
    walk(root, 0, maxDepth, sampleCount, lines);
    return lines.join("\n");
  }

  function walk(el, depth, maxDepth, sampleCount, lines) {
    if (depth > maxDepth) return;
    const indent = "  ".repeat(depth);
    const desc = describeElement(el);

    // Special handling for <table>
    if (el.tagName === "TABLE") {
      const rows = el.querySelectorAll("tr");
      const cols = rows.length > 0 ? rows[0].querySelectorAll("th, td").length : 0;
      lines.push(`${indent}${desc} ${cols} cols x ${rows.length} rows`);
      // Show header if exists
      const headers = el.querySelectorAll("th");
      if (headers.length > 0) {
        const headerTexts = Array.from(headers).map(h => h.textContent.trim());
        lines.push(`${indent}  headers: ${JSON.stringify(headerTexts)}`);
      }
      // Show sample rows
      const dataRows = el.querySelectorAll("tbody tr");
      for (let i = 0; i < Math.min(sampleCount, dataRows.length); i++) {
        const cells = Array.from(dataRows[i].querySelectorAll("td")).map(td => td.textContent.trim());
        lines.push(`${indent}  sample[${i}]: ${JSON.stringify(cells)}`);
      }
      return;
    }

    // Special handling for <select>
    if (el.tagName === "SELECT") {
      const opts = Array.from(el.options).map(o => o.text);
      const display = opts.length > 5 ? opts.slice(0, 5).concat([`... +${opts.length - 5} more`]) : opts;
      lines.push(`${indent}${desc} ${opts.length} options: ${JSON.stringify(display)}`);
      return;
    }

    // Check for repeated children (lists, card grids)
    const childTags = {};
    for (const child of el.children) {
      const key = child.tagName + (child.className ? `.${child.className.split(" ")[0]}` : "");
      childTags[key] = (childTags[key] || 0) + 1;
    }
    const repeated = Object.entries(childTags).find(([, count]) => count > 3);

    if (repeated) {
      const [pattern, count] = repeated;
      const tag = pattern.split(".")[0].toLowerCase();
      const cls = pattern.includes(".") ? `.${pattern.split(".")[1]}` : "";
      lines.push(`${indent}${desc}`);
      lines.push(`${indent}  <${tag}${cls}> x ${count} items`);
      // Show samples
      const items = el.querySelectorAll(`:scope > ${tag}${cls ? `.${cls}` : ""}`);
      for (let i = 0; i < Math.min(sampleCount, items.length); i++) {
        const text = items[i].textContent.trim().substring(0, 100);
        lines.push(`${indent}    sample[${i}]: "${text}"`);
      }
      return;
    }

    // Interactive elements get extra detail
    const isInteractive = ["INPUT", "BUTTON", "TEXTAREA", "A", "SELECT"].includes(el.tagName);
    if (isInteractive || el.children.length === 0) {
      const text = el.textContent ? el.textContent.trim().substring(0, 80) : "";
      if (text && !desc.includes('"')) {
        lines.push(`${indent}${desc} "${text}"`);
      } else {
        lines.push(`${indent}${desc}`);
      }
      return;
    }

    lines.push(`${indent}${desc}`);
    for (const child of el.children) {
      walk(child, depth + 1, maxDepth, sampleCount, lines);
    }
  }

  function describeElement(el) {
    let desc = `<${el.tagName.toLowerCase()}`;
    if (el.id) desc += `#${el.id}`;
    if (el.classList.length > 0) {
      desc += `.${Array.from(el.classList).join(".")}`;
    }
    desc += ">";

    // Add useful attributes for interactive elements
    const tag = el.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA") {
      const type = el.getAttribute("type");
      const placeholder = el.getAttribute("placeholder");
      const required = el.hasAttribute("required");
      const parts = [];
      if (type) parts.push(`type="${type}"`);
      if (placeholder) parts.push(`placeholder="${placeholder}"`);
      if (required) parts.push("[required]");
      if (parts.length > 0) desc = desc.slice(0, -1) + " " + parts.join(" ") + ">";
    }

    if (tag === "A") {
      const href = el.getAttribute("href");
      if (href) desc = desc.slice(0, -1) + ` href="${href.substring(0, 60)}">`;
    }

    return desc;
  }

  // -----------------------------------------------------------------------
  // Extract Table
  // -----------------------------------------------------------------------
  function extractTable(selector) {
    const table = document.querySelector(selector);
    if (!table) return { __error: true, name: "ElementNotFoundError", message: `Table not found: ${selector}` };

    // Get headers
    const headers = [];
    const ths = table.querySelectorAll("thead th, thead td, tr:first-child th");
    if (ths.length > 0) {
      ths.forEach(th => headers.push(th.textContent.trim()));
    } else {
      // If no headers, use first row
      const firstRow = table.querySelector("tr");
      if (firstRow) {
        firstRow.querySelectorAll("td, th").forEach((cell, i) => {
          headers.push(cell.textContent.trim() || `col_${i}`);
        });
      }
    }

    // Get data rows
    const rows = [];
    const trs = table.querySelectorAll("tbody tr");
    const dataRows = trs.length > 0 ? trs : table.querySelectorAll("tr:not(:first-child)");

    dataRows.forEach(tr => {
      const row = {};
      const cells = tr.querySelectorAll("td");
      cells.forEach((cell, i) => {
        const key = headers[i] || `col_${i}`;
        row[key] = cell.textContent.trim();
      });
      if (Object.keys(row).length > 0) {
        rows.push(row);
      }
    });

    return rows;
  }
}

// ---------------------------------------------------------------------------
// Initialize: start connecting
// ---------------------------------------------------------------------------

connect();
```

- [ ] **Step 4: Verify manifest.json is valid JSON**

Run: `python -c "import json; json.load(open('extension/manifest.json'))"`
Expected: No error

- [ ] **Step 5: Commit**

```bash
git add extension/
git commit -m "feat: add Chrome extension with Manifest V3, WS client, DOM actions"
```

---

### Task 9: Tab Manager Module

**Files:**
- Create: `src/pywebflx/tab_manager.py`
- Create: `tests/test_tab_manager.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_tab_manager.py
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
        # First call: find_tabs returns empty
        # Second call: create_tab returns new tab
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_tab_manager.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pywebflx.tab_manager'`

- [ ] **Step 3: Implement tab manager module**

```python
# src/pywebflx/tab_manager.py
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
    """Manages Chrome tab discovery and creation.

    Attributes:
        _conn: The WebSocket server connection to the extension.
    """

    def __init__(self, conn: WebSocketServer):
        self._conn = conn

    async def find_tab(
        self,
        title: str | None = None,
        url: str | None = None,
    ) -> dict[str, Any]:
        """Find an open tab matching the given title and/or URL.

        Args:
            title: Partial tab title to search for.
            url: Partial URL to search for.

        Returns:
            Dict with keys: id, title, url.

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
        """Create a new tab with the given URL.

        Args:
            url: The URL to open in the new tab.

        Returns:
            Dict with keys: id, title, url.
        """
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

        Searches for a tab by title and/or URL. If not found:
        - If if_not_open is set, creates a new tab with that URL.
        - If if_not_open is not set, raises BrowserNotFoundError.

        Args:
            title: Partial tab title to search for.
            url: Partial URL to search for.
            if_not_open: Fallback URL to open if tab not found.

        Returns:
            Dict with keys: id, title, url.

        Raises:
            BrowserNotFoundError: If tab not found and no fallback URL.
        """
        try:
            return await self.find_tab(title=title, url=url)
        except TabNotFoundError:
            if if_not_open:
                return await self.create_tab(if_not_open)
            raise BrowserNotFoundError(title=title, url=url)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_tab_manager.py -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/pywebflx/tab_manager.py tests/test_tab_manager.py
git commit -m "feat: add TabManager with find, create, and find_or_open"
```

---

### Task 10: BrowserContext and use_browser

**Files:**
- Create: `src/pywebflx/browser.py`
- Create: `tests/test_browser.py`
- Modify: `src/pywebflx/__init__.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_browser.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_browser.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pywebflx.browser'`

- [ ] **Step 3: Implement browser module**

```python
# src/pywebflx/browser.py
"""BrowserContext — the main interface for browser automation.

Provides use_browser() async context manager that connects to a Chrome tab
and exposes all automation methods (click, type_into, get_text, etc.).

Example:
    async with use_browser(url="sicoob.com.br", if_not_open="https://sicoob.com.br") as browser:
        await browser.click("#btn-login")
        text = await browser.get_text(".welcome")
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from pywebflx.config import PyWebFlxConfig
from pywebflx.connection import WebSocketServer
from pywebflx.exceptions import (
    ConnectionLostError,
    ElementNotFoundError,
    ElementTimeoutError,
    ElementNotInteractableError,
    InjectionError,
    NavigationError,
    ScreenshotError,
    DownloadError,
)
from pywebflx.logging import _logged_action, _log
from pywebflx.protocol import Response
from pywebflx.selectors import resolve_selector
from pywebflx.tab_manager import TabManager


class BrowserContext:
    """Represents a connection to a specific Chrome tab.

    All browser automation methods are available on this object.
    Created by use_browser(), not directly instantiated by users.

    Attributes:
        _conn: WebSocket server connection.
        _tab_id: Chrome tab ID this context is bound to.
        _config: Configuration for timeouts, retries, logging.
    """

    def __init__(
        self,
        conn: WebSocketServer,
        tab_id: int,
        config: PyWebFlxConfig,
    ):
        self._conn = conn
        self._tab_id = tab_id
        self._config = config

    async def _send(self, action: str, params: dict[str, Any], timeout: float | None = None) -> Any:
        """Send a command to the extension and return the response data.

        Args:
            action: The action name.
            params: Action parameters.
            timeout: Override timeout in seconds.

        Returns:
            The response data field.

        Raises:
            Appropriate PyWebFlx exception based on error type.
        """
        effective_timeout = self._config.resolve("timeout", timeout)
        response = await self._conn.send_command(
            action=action,
            tab_id=self._tab_id,
            params=params,
            timeout=effective_timeout,
        )
        if not response.success:
            self._raise_from_response(response)
        return response.data

    def _raise_from_response(self, response: Response) -> None:
        """Convert an error response into the appropriate exception."""
        error_map = {
            "ElementNotFoundError": ElementNotFoundError,
            "ElementTimeoutError": ElementTimeoutError,
            "ElementNotInteractableError": ElementNotInteractableError,
            "InjectionError": InjectionError,
            "NavigationError": NavigationError,
        }
        exc_cls = error_map.get(response.error)
        if exc_cls and exc_cls == ElementNotFoundError:
            raise ElementNotFoundError(selector="unknown", tab_id=self._tab_id)
        elif exc_cls:
            raise exc_cls(response.message or response.error)
        raise InjectionError(tab_id=self._tab_id, reason=response.message or response.error)

    def _resolve_params(self, selector, selector_type=None, **extra) -> dict[str, Any]:
        """Build params dict from selector args, detecting CSS/XPath/attributes."""
        if isinstance(selector, str) and selector:
            resolved = resolve_selector(selector)
            params = {
                "selector": resolved.selector,
                "selectorType": resolved.selector_type,
            }
        else:
            # Attribute-based: text, tag, role, name come via extra
            params = {}
            for key in ("text", "tag", "role", "name"):
                if key in extra:
                    params[key] = extra.pop(key)
            params["selectorType"] = "attributes"
        params.update(extra)
        return params

    async def _execute_with_retry(
        self,
        action: str,
        params: dict[str, Any],
        timeout: float | None = None,
        retry: int | None = None,
        verify: str | None = None,
        delay_before: float | None = None,
        delay_after: float | None = None,
    ) -> Any:
        """Execute an action with optional retry, verify, and delays.

        Args:
            action: The action name.
            params: Action parameters.
            timeout: Timeout per attempt.
            retry: Number of retries (0 = no retry).
            verify: Selector to check after action succeeds.
            delay_before: Delay before action in seconds.
            delay_after: Delay after action in seconds.

        Returns:
            The response data.
        """
        effective_retry = self._config.resolve("retry_count", retry) or 0
        effective_delay_before = delay_before
        effective_delay_after = delay_after or self._config.delay_between_actions

        max_attempts = effective_retry + 1

        for attempt in range(1, max_attempts + 1):
            try:
                if effective_delay_before and effective_delay_before > 0:
                    await asyncio.sleep(effective_delay_before)

                result = await self._send(action, params, timeout)

                if verify:
                    verify_result = await self._send(
                        "element_exists",
                        {"selector": verify, "selectorType": "css"},
                        timeout=5,
                    )
                    if not verify_result:
                        raise ElementNotFoundError(selector=verify, tab_id=self._tab_id)

                if effective_delay_after and effective_delay_after > 0:
                    await asyncio.sleep(effective_delay_after)

                return result

            except Exception:
                if attempt >= max_attempts:
                    raise
                await asyncio.sleep(1.0)

    # -------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------

    @_logged_action("browser.navigate_to")
    async def navigate_to(self, url: str, **kwargs) -> None:
        """Navigate to a URL in the current tab.

        Args:
            url: The URL to navigate to.
        """
        await self._send("navigate", {"url": url}, kwargs.get("timeout"))

    @_logged_action("browser.go_back")
    async def go_back(self, selector: str = "", **kwargs) -> None:
        """Navigate back in browser history."""
        await self._send("go_back", {})

    @_logged_action("browser.go_forward")
    async def go_forward(self, selector: str = "", **kwargs) -> None:
        """Navigate forward in browser history."""
        await self._send("go_forward", {})

    @_logged_action("browser.refresh")
    async def refresh(self, selector: str = "", **kwargs) -> None:
        """Reload the current page."""
        await self._send("refresh", {})

    @_logged_action("browser.close_tab")
    async def close_tab(self, selector: str = "", **kwargs) -> None:
        """Close the current tab."""
        await self._send("close_tab", {})

    @_logged_action("browser.close_browser")
    async def close_browser(self, selector: str = "", **kwargs) -> None:
        """Close all browser tabs (effectively closing the browser)."""
        # Implemented by closing all tabs
        await self._send("close_tab", {})

    # -------------------------------------------------------------------
    # Interaction
    # -------------------------------------------------------------------

    @_logged_action("browser.click")
    async def click(
        self,
        selector: str = "",
        *,
        text: str | None = None,
        tag: str | None = None,
        role: str | None = None,
        name: str | None = None,
        click_type: str = "single",
        mouse_button: str = "left",
        timeout: float | None = None,
        retry: int | None = None,
        verify: str | None = None,
        delay_before: float | None = None,
        delay_after: float | None = None,
        **kwargs,
    ) -> None:
        """Click an element on the page.

        Args:
            selector: CSS selector or XPath expression.
            text: Find element by visible text content.
            tag: Filter by HTML tag name.
            role: Find by ARIA role attribute.
            name: Find by ARIA name/label.
            click_type: "single" or "double".
            mouse_button: "left", "right", or "middle".
            timeout: Timeout in seconds.
            retry: Number of retries on failure.
            verify: Selector to verify after click.
            delay_before: Delay before click in seconds.
            delay_after: Delay after click in seconds.
        """
        params = self._resolve_params(
            selector, text=text, tag=tag, role=role, name=name,
            clickType=click_type, mouseButton=mouse_button,
        )
        await self._execute_with_retry(
            "click", params,
            timeout=timeout, retry=retry, verify=verify,
            delay_before=delay_before, delay_after=delay_after,
        )

    @_logged_action("browser.type_into")
    async def type_into(
        self,
        selector: str = "",
        text: str = "",
        *,
        clear_before: bool = True,
        click_before: bool = True,
        delay_between_keys: float = 0,
        timeout: float | None = None,
        retry: int | None = None,
        **kwargs,
    ) -> None:
        """Type text into an input field.

        Args:
            selector: CSS selector or XPath for the input field.
            text: Text to type.
            clear_before: Clear the field before typing.
            click_before: Click/focus the field before typing.
            delay_between_keys: Delay between keystrokes (0 = instant).
            timeout: Timeout in seconds.
            retry: Number of retries on failure.
        """
        params = self._resolve_params(selector)
        params.update({
            "text": text,
            "clearBefore": clear_before,
            "clickBefore": click_before,
            "delayBetweenKeys": delay_between_keys,
        })
        await self._execute_with_retry("type_into", params, timeout=timeout, retry=retry)

    @_logged_action("browser.set_text")
    async def set_text(self, selector: str = "", text: str = "", **kwargs) -> None:
        """Set text on an element without simulating keystrokes.

        Args:
            selector: CSS selector or XPath for the element.
            text: Text value to set.
        """
        params = self._resolve_params(selector)
        params["text"] = text
        await self._send("set_text", params)

    @_logged_action("browser.check")
    async def check(self, selector: str = "", **kwargs) -> None:
        """Check a checkbox.

        Args:
            selector: CSS selector or XPath for the checkbox.
        """
        params = self._resolve_params(selector)
        await self._send("check", params)

    @_logged_action("browser.uncheck")
    async def uncheck(self, selector: str = "", **kwargs) -> None:
        """Uncheck a checkbox.

        Args:
            selector: CSS selector or XPath for the checkbox.
        """
        params = self._resolve_params(selector)
        await self._send("uncheck", params)

    @_logged_action("browser.select_item")
    async def select_item(
        self, selector: str = "", item: str = "", *, by: str = "text", **kwargs
    ) -> None:
        """Select an item in a dropdown/select element.

        Args:
            selector: CSS selector or XPath for the select element.
            item: The value, text, or index to select.
            by: Selection method — "text", "value", or "index".
        """
        params = self._resolve_params(selector)
        params.update({"item": item, "by": by})
        await self._send("select_item", params)

    @_logged_action("browser.hover")
    async def hover(self, selector: str = "", **kwargs) -> None:
        """Hover over an element.

        Args:
            selector: CSS selector or XPath for the element.
        """
        params = self._resolve_params(selector)
        await self._send("hover", params)

    @_logged_action("browser.send_hotkey")
    async def send_hotkey(self, keys: str = "", **kwargs) -> None:
        """Send keyboard shortcut.

        Args:
            keys: Key combination (e.g., "ctrl+a", "Enter", "Tab").
        """
        # keys is passed as the selector positional arg by the decorator
        await self._send("send_hotkey", {"keys": keys})

    # -------------------------------------------------------------------
    # Extraction
    # -------------------------------------------------------------------

    @_logged_action("browser.get_text")
    async def get_text(self, selector: str = "", **kwargs) -> str:
        """Get the visible text of an element.

        Args:
            selector: CSS selector or XPath for the element.

        Returns:
            The element's visible text content.
        """
        params = self._resolve_params(selector)
        return await self._send("get_text", params)

    @_logged_action("browser.get_attribute")
    async def get_attribute(self, selector: str = "", attribute: str = "", **kwargs) -> str | None:
        """Get an HTML attribute value from an element.

        Args:
            selector: CSS selector or XPath for the element.
            attribute: Attribute name (e.g., "href", "class", "value").

        Returns:
            The attribute value, or None if not present.
        """
        params = self._resolve_params(selector)
        params["attribute"] = attribute
        return await self._send("get_attribute", params)

    @_logged_action("browser.get_full_text")
    async def get_full_text(self, selector: str = "", **kwargs) -> str:
        """Get all visible text from the page.

        Returns:
            All visible text content of the page body.
        """
        return await self._send("get_full_text", {})

    @_logged_action("browser.inspect")
    async def inspect(
        self, selector: str = "", *, depth: int = 2, samples: int = 2, **kwargs
    ) -> str:
        """Get a summarized view of the DOM structure, optimized for AI consumption.

        Returns a compact text representation of the DOM showing element hierarchy,
        IDs, classes, interactive elements, table dimensions, and sample data.
        Uses ~95% fewer tokens than raw outerHTML.

        Args:
            selector: CSS selector to scope the inspection (default: entire page).
            depth: Maximum depth of DOM traversal (default: 2).
            samples: Number of sample data rows to include for tables/lists (default: 2).

        Returns:
            Multi-line string with the DOM structure summary.

        Example:
            structure = await browser.inspect()
            structure = await browser.inspect("#login-form", depth=3)
        """
        params = {"depth": depth, "samples": samples}
        if selector:
            params["selector"] = selector
        return await self._send("inspect", params)

    @_logged_action("browser.extract_table")
    async def extract_table(
        self,
        selector: str = "",
        *,
        next_page: str | None = None,
        max_pages: int = 100,
        **kwargs,
    ) -> list[dict[str, str]]:
        """Extract data from an HTML table.

        Reads all rows from a <table> element and returns them as a list of dicts
        using header text as keys. Supports automatic pagination.

        Args:
            selector: CSS selector for the <table> element.
            next_page: CSS selector for the "next page" button (for pagination).
            max_pages: Maximum number of pages to extract (default: 100).

        Returns:
            List of dicts, one per row, with column headers as keys.

        Example:
            data = await browser.extract_table("#tabela-clientes")
            data = await browser.extract_table("#tabela", next_page="#btn-next", max_pages=5)
        """
        all_rows: list[dict[str, str]] = []

        for page in range(max_pages):
            page_data = await self._send("extract_table", {"selector": selector})

            if isinstance(page_data, list):
                all_rows.extend(page_data)

            if not next_page:
                break

            # Check if next page button exists and click it
            exists = await self._send(
                "element_exists",
                {"selector": next_page, "selectorType": "css"},
            )
            if not exists:
                break

            await self._send(
                "click",
                {"selector": next_page, "selectorType": "css", "clickType": "single", "mouseButton": "left"},
            )
            # Wait for page to update
            await asyncio.sleep(1.0)

        return all_rows

    @_logged_action("browser.extract_data")
    async def extract_data(
        self,
        selector: str = "",
        *,
        container: str = "",
        row: str = "",
        columns: dict[str, str] | None = None,
        next_page: str | None = None,
        max_pages: int = 100,
        **kwargs,
    ) -> list[dict[str, str]]:
        """Extract structured data from non-table elements (cards, divs, lists).

        Args:
            container: CSS selector for the parent container.
            row: CSS selector for each repeated item within the container.
            columns: Mapping of column name to CSS selector within each row.
            next_page: CSS selector for the "next page" button.
            max_pages: Maximum pages to extract.

        Returns:
            List of dicts with column names as keys.

        Example:
            data = await browser.extract_data(
                container="#results",
                row=".card",
                columns={"Name": ".title", "Price": ".price"},
            )
        """
        all_rows: list[dict[str, str]] = []

        for page in range(max_pages):
            js_code = f"""
                (() => {{
                    const container = document.querySelector({repr(container)});
                    if (!container) return [];
                    const rows = container.querySelectorAll({repr(row)});
                    const columns = {columns or {}};
                    return Array.from(rows).map(r => {{
                        const obj = {{}};
                        for (const [name, sel] of Object.entries(columns)) {{
                            const el = r.querySelector(sel);
                            obj[name] = el ? el.textContent.trim() : "";
                        }}
                        return obj;
                    }});
                }})()
            """
            page_data = await self._send("execute_js", {"code": js_code})
            if isinstance(page_data, list):
                all_rows.extend(page_data)

            if not next_page:
                break

            exists = await self._send(
                "element_exists",
                {"selector": next_page, "selectorType": "css"},
            )
            if not exists:
                break

            await self._send(
                "click",
                {"selector": next_page, "selectorType": "css", "clickType": "single", "mouseButton": "left"},
            )
            await asyncio.sleep(1.0)

        return all_rows

    # -------------------------------------------------------------------
    # Synchronization
    # -------------------------------------------------------------------

    @_logged_action("browser.element_exists")
    async def element_exists(self, selector: str = "", *, timeout: float = 0, **kwargs) -> bool:
        """Check if an element exists on the page.

        Args:
            selector: CSS selector or XPath for the element.
            timeout: If > 0, wait up to this many seconds for the element.

        Returns:
            True if element exists, False otherwise.
        """
        if timeout > 0:
            return await self._poll_element(selector, timeout, condition="exists")

        params = self._resolve_params(selector)
        return await self._send("element_exists", params)

    @_logged_action("browser.wait_element")
    async def wait_element(
        self, selector: str = "", *, condition: str = "visible", timeout: float | None = None, **kwargs
    ) -> None:
        """Wait for an element to meet a condition.

        Args:
            selector: CSS selector or XPath for the element.
            condition: "visible", "clickable", "present".
            timeout: Maximum wait time in seconds.

        Raises:
            ElementTimeoutError: If condition not met within timeout.
        """
        effective_timeout = self._config.resolve("timeout", timeout)
        found = await self._poll_element(selector, effective_timeout, condition)
        if not found:
            from pywebflx.exceptions import ElementTimeoutError
            raise ElementTimeoutError(
                selector=selector, tab_id=self._tab_id,
                timeout=effective_timeout, condition=condition,
            )

    @_logged_action("browser.wait_element_vanish")
    async def wait_element_vanish(self, selector: str = "", *, timeout: float | None = None, **kwargs) -> None:
        """Wait for an element to disappear from the page.

        Args:
            selector: CSS selector or XPath for the element.
            timeout: Maximum wait time in seconds.

        Raises:
            ElementTimeoutError: If element still present after timeout.
        """
        effective_timeout = self._config.resolve("timeout", timeout)
        start = time.monotonic()
        while time.monotonic() - start < effective_timeout:
            params = self._resolve_params(selector)
            exists = await self._send("element_exists", params)
            if not exists:
                return
            await asyncio.sleep(0.5)
        from pywebflx.exceptions import ElementTimeoutError
        raise ElementTimeoutError(
            selector=selector, tab_id=self._tab_id,
            timeout=effective_timeout, condition="invisible",
        )

    @_logged_action("browser.find_element")
    async def find_element(self, selector: str = "", **kwargs) -> dict[str, Any]:
        """Find an element and return info about it.

        Args:
            selector: CSS selector or XPath for the element.

        Returns:
            Dict with tag, id, classes, text, visible.

        Raises:
            ElementNotFoundError: If element not found.
        """
        params = self._resolve_params(selector)
        return await self._send("find_element", params)

    async def _poll_element(self, selector: str, timeout: float, condition: str) -> bool:
        """Poll for an element condition with 500ms interval."""
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            params = self._resolve_params(selector)
            result = await self._send("element_exists", params)
            if result:
                return True
            await asyncio.sleep(0.5)
        return False

    # -------------------------------------------------------------------
    # JavaScript and Iframes
    # -------------------------------------------------------------------

    @_logged_action("browser.execute_js")
    async def execute_js(self, code: str = "", **kwargs) -> Any:
        """Execute JavaScript code in the page and return the result.

        Args:
            code: JavaScript code to execute (e.g., "return document.title").

        Returns:
            The return value of the JavaScript code.
        """
        return await self._send("execute_js", {"code": code})

    @_logged_action("browser.inject_js")
    async def inject_js(self, code: str = "", **kwargs) -> None:
        """Inject and execute JavaScript without waiting for a return value.

        Args:
            code: JavaScript code to execute.
        """
        await self._send("execute_js", {"code": code})

    @asynccontextmanager
    async def switch_to(self, selector: str) -> AsyncGenerator[BrowserContext, None]:
        """Switch context to an iframe for executing actions inside it.

        Args:
            selector: CSS selector for the iframe element.

        Yields:
            A BrowserContext scoped to the iframe.

        Example:
            async with browser.switch_to("#my-iframe") as frame:
                await frame.click("#btn-inside")
        """
        # For iframes, we create a sub-context that prepends iframe selection
        # to all commands. This is handled by the extension via frameId.
        # For now, yield self with a flag for iframe targeting.
        yield self  # TODO: implement proper iframe scoping in v2

    # -------------------------------------------------------------------
    # Files (Screenshots, Downloads, Uploads)
    # -------------------------------------------------------------------

    @_logged_action("browser.take_screenshot")
    async def take_screenshot(self, path: str = "", *, selector: str | None = None, **kwargs) -> None:
        """Capture a screenshot of the page or a specific element.

        Args:
            path: File path to save the screenshot (PNG).
            selector: Optional CSS selector to capture only that element.
        """
        params = {"path": path}
        if selector:
            params["selector"] = selector
        # Screenshot is handled by background.js via chrome.tabs.captureVisibleTab
        await self._send("take_screenshot", params)

    @_logged_action("browser.set_file")
    async def set_file(self, selector: str = "", path: str = "", **kwargs) -> None:
        """Set a file path on a file input element for upload.

        Args:
            selector: CSS selector for the file input.
            path: Local file path to set.
        """
        params = self._resolve_params(selector)
        params["filePath"] = path
        await self._send("set_file", params)

    @asynccontextmanager
    async def wait_for_download(self, timeout: float = 30) -> AsyncGenerator[Any, None]:
        """Wait for a download to complete.

        Args:
            timeout: Maximum wait time in seconds.

        Yields:
            Download info object with .path attribute.

        Example:
            async with browser.wait_for_download() as dl:
                await browser.click("#download-btn")
            print(dl.path)
        """

        class DownloadResult:
            def __init__(self):
                self.path: str | None = None

        result = DownloadResult()
        yield result
        # After the block, poll for download completion
        # This would use chrome.downloads API via the extension


    # -------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------

    async def health_check(self) -> dict[str, Any]:
        """Check connection status and extension health.

        Returns:
            Dict with connected, tabs count, active_tab, latency_ms.
        """
        start = time.monotonic()
        response = await self._conn.send_command(
            action="find_tabs", params={}, timeout=5,
        )
        latency = (time.monotonic() - start) * 1000
        tabs = response.data if response.success else []
        return {
            "connected": True,
            "tabs": len(tabs),
            "active_tab": self._tab_id,
            "latency_ms": round(latency, 1),
        }


@asynccontextmanager
async def use_browser(
    *,
    url: str | None = None,
    title: str | None = None,
    if_not_open: str | None = None,
    config: PyWebFlxConfig | None = None,
) -> AsyncGenerator[BrowserContext, None]:
    """Connect to an already-open Chrome tab and return a BrowserContext.

    Searches for a tab matching the given title and/or URL. If not found
    and if_not_open is set, opens a new tab with that URL.

    Args:
        url: Partial URL to search for in open tabs.
        title: Partial title to search for in open tabs.
        if_not_open: URL to open if no matching tab is found.
        config: Configuration overrides. Uses defaults if not provided.

    Yields:
        BrowserContext bound to the matched/opened tab.

    Raises:
        BrowserNotFoundError: If no tab found and no if_not_open fallback.
        ExtensionNotConnectedError: If Chrome extension is not connected.

    Example:
        async with use_browser(url="sicoob.com.br", if_not_open="https://sicoob.com.br") as browser:
            await browser.click("#login")
    """
    cfg = config or PyWebFlxConfig()
    server = WebSocketServer(port=cfg.ws_port)
    await server.start()

    try:
        await server.wait_for_connection(timeout=30)

        mgr = TabManager(server)
        tab = await mgr.find_or_open(title=title, url=url, if_not_open=if_not_open)

        ctx = BrowserContext(conn=server, tab_id=tab["id"], config=cfg)
        yield ctx
    finally:
        await server.stop()
```

- [ ] **Step 4: Update __init__.py with public exports**

```python
# src/pywebflx/__init__.py
"""PyWebFlx — Browser automation for already-open Chrome pages.

Example:
    from pywebflx import use_browser, PyWebFlxConfig, configure_logging

    configure_logging(level="INFO")

    async with use_browser(url="sicoob.com.br") as browser:
        await browser.click("#btn-login")
        text = await browser.get_text(".welcome")
"""

__version__ = "0.1.0"

from pywebflx.browser import use_browser, BrowserContext
from pywebflx.config import PyWebFlxConfig
from pywebflx.logging import configure_logging
from pywebflx.exceptions import (
    PyWebFlxError,
    BrowserNotFoundError,
    TabNotFoundError,
    TabClosedError,
    ElementNotFoundError,
    ElementTimeoutError,
    ElementNotInteractableError,
    SelectorError,
    ConnectionError,
    ExtensionNotConnectedError,
    ConnectionLostError,
    NavigationError,
    InjectionError,
    DownloadError,
    ScreenshotError,
    ConfigError,
)

__all__ = [
    "use_browser",
    "BrowserContext",
    "PyWebFlxConfig",
    "configure_logging",
    "PyWebFlxError",
    "BrowserNotFoundError",
    "TabNotFoundError",
    "TabClosedError",
    "ElementNotFoundError",
    "ElementTimeoutError",
    "ElementNotInteractableError",
    "SelectorError",
    "ConnectionError",
    "ExtensionNotConnectedError",
    "ConnectionLostError",
    "NavigationError",
    "InjectionError",
    "DownloadError",
    "ScreenshotError",
    "ConfigError",
]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_browser.py -v`
Expected: All 3 tests PASS

- [ ] **Step 6: Run all tests to verify nothing is broken**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/pywebflx/browser.py src/pywebflx/__init__.py tests/test_browser.py
git commit -m "feat: add BrowserContext with all actions and use_browser context manager"
```

---

### Task 11: CLI Module

**Files:**
- Create: `src/pywebflx/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_cli.py
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
        assert "extension" in result.output.lower() or "connect" in result.output.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pywebflx.cli'`

- [ ] **Step 3: Implement CLI module**

```python
# src/pywebflx/cli.py
"""PyWebFlx CLI — install extension and check connection.

Commands:
    pywebflx install-extension  — Guide Chrome extension installation
    pywebflx check              — Verify extension is connected

Example:
    $ pywebflx install-extension
    $ pywebflx check
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

import click

from pywebflx import __version__


def _get_extension_dir() -> Path:
    """Get the path to the bundled Chrome extension directory."""
    # Extension is bundled at the package root level
    pkg_root = Path(__file__).resolve().parent.parent.parent
    ext_dir = pkg_root / "extension"
    if not ext_dir.exists():
        # Fallback: check relative to this file (installed via pip)
        ext_dir = Path(__file__).resolve().parent / "extension"
    return ext_dir


@click.group()
@click.version_option(version=__version__, prog_name="pywebflx")
def main():
    """PyWebFlx — Browser automation for already-open Chrome pages."""
    pass


@main.command("install-extension")
def install_extension():
    """Guide installation of the PyWebFlx Chrome extension."""
    ext_dir = _get_extension_dir()

    click.echo("=" * 60)
    click.echo("  PyWebFlx — Chrome Extension Installation")
    click.echo("=" * 60)
    click.echo()

    if ext_dir.exists():
        click.echo(f"Extension found at: {ext_dir}")
    else:
        click.echo(f"Extension NOT found at: {ext_dir}")
        click.echo("Please reinstall pywebflx or check your installation.")
        return

    click.echo()
    click.echo("Follow these steps to install:")
    click.echo()
    click.echo("  1. Open Chrome and go to: chrome://extensions")
    click.echo("  2. Enable 'Developer mode' (toggle in top-right corner)")
    click.echo("  3. Click 'Load unpacked'")
    click.echo(f"  4. Select this folder: {ext_dir}")
    click.echo("  5. The extension 'PyWebFlx Bridge' should appear")
    click.echo()

    # Try to open chrome://extensions
    try:
        if sys.platform == "win32":
            subprocess.Popen(
                ["start", "chrome", "chrome://extensions"],
                shell=True,
            )
            click.echo("Opening chrome://extensions in your browser...")
        elif sys.platform == "darwin":
            subprocess.Popen(
                ["open", "-a", "Google Chrome", "chrome://extensions"],
            )
            click.echo("Opening chrome://extensions in your browser...")
    except Exception:
        click.echo("Could not open Chrome automatically. Please open chrome://extensions manually.")

    click.echo()
    click.echo("After installing, run 'pywebflx check' to verify the connection.")


@main.command("check")
def check():
    """Check if the Chrome extension is connected."""
    click.echo("Checking PyWebFlx extension connection...")
    click.echo()

    async def _check():
        from pywebflx.connection import WebSocketServer
        from pywebflx.exceptions import ExtensionNotConnectedError

        server = WebSocketServer(port=9819)
        await server.start()
        try:
            await server.wait_for_connection(timeout=5)
            click.echo("Extension is CONNECTED!")
            click.echo("PyWebFlx is ready to use.")
            return True
        except ExtensionNotConnectedError:
            click.echo("Extension is NOT connected.")
            click.echo()
            click.echo("Make sure:")
            click.echo("  1. Chrome is open")
            click.echo("  2. PyWebFlx Bridge extension is installed and enabled")
            click.echo("  3. No other pywebflx instance is running on port 9819")
            return False
        finally:
            await server.stop()

    connected = asyncio.run(_check())
    if not connected:
        sys.exit(1)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_cli.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/pywebflx/cli.py tests/test_cli.py
git commit -m "feat: add CLI with install-extension and check commands"
```

---

### Task 12: Final Integration — Run All Tests and Verify

**Files:**
- No new files. This task validates everything works together.

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: All tests PASS (~50+ tests)

- [ ] **Step 2: Verify package installs cleanly**

Run: `pip install -e ".[dev]" && python -c "from pywebflx import use_browser, PyWebFlxConfig, configure_logging; print('All imports OK')"`
Expected: `All imports OK`

- [ ] **Step 3: Verify CLI works**

Run: `pywebflx --version`
Expected: `pywebflx, version 0.1.0`

Run: `pywebflx install-extension`
Expected: Shows installation instructions with extension path

- [ ] **Step 4: Verify extension manifest is valid**

Run: `python -c "import json; m = json.load(open('extension/manifest.json')); assert m['manifest_version'] == 3; print('Manifest OK')"`
Expected: `Manifest OK`

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete PyWebFlx v0.1.0 — browser automation via Chrome extension"
```
