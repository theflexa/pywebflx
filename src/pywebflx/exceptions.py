"""PyWebFlx exception hierarchy.

All exceptions inherit from PyWebFlxError. Each exception carries
contextual attributes relevant to the error (selector, tab_id, timeout, etc.)
so callers can inspect what went wrong programmatically.

Hierarchy:
    PyWebFlxError
    +-- ConnectionError
    |   +-- ExtensionNotConnectedError
    |   +-- ConnectionLostError
    +-- BrowserError
    |   +-- BrowserNotFoundError
    |   +-- TabNotFoundError
    |   +-- TabClosedError
    +-- ElementError
    |   +-- ElementNotFoundError
    |   +-- ElementTimeoutError
    |   +-- ElementNotInteractableError
    |   +-- SelectorError
    +-- ActionError
    |   +-- NavigationError
    |   +-- InjectionError
    |   +-- DownloadError
    |   +-- ScreenshotError
    +-- ConfigError
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
    """Chrome extension has not connected to the WebSocket server."""

    def __init__(self, port: int = 9819, timeout: float = 30):
        self.port = port
        self.timeout = timeout
        super().__init__(
            f"Extension did not connect to ws://localhost:{port} within {timeout}s"
        )


class ConnectionLostError(ConnectionError):
    """WebSocket connection was lost during operation."""

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
    """Chrome browser is not running or no matching tab was found."""

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
    """Specific tab was not found by title or URL."""

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
    """Target tab was closed during operation."""

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
    """Selector did not match any element."""

    def __init__(self, selector: str, tab_id: int | None = None, timeout: float = 10):
        self.selector = selector
        self.tab_id = tab_id
        self.timeout = timeout
        super().__init__(
            f"Element '{selector}' not found within {timeout}s (tab:{tab_id})"
        )


class ElementTimeoutError(ElementError):
    """Timed out waiting for element condition."""

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
    """Element exists but cannot be interacted with."""

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
    """Invalid selector syntax."""

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
    """Failed to navigate to URL."""

    def __init__(self, url: str, reason: str = "navigation failed"):
        self.url = url
        self.reason = reason
        super().__init__(f"Navigation to '{url}' failed: {reason}")


class InjectionError(ActionError):
    """Failed to inject or execute script in tab."""

    def __init__(self, tab_id: int | None = None, reason: str = "injection failed"):
        self.tab_id = tab_id
        self.reason = reason
        super().__init__(f"Script injection failed in tab:{tab_id}: {reason}")


class DownloadError(ActionError):
    """Download failed or timed out."""

    def __init__(self, timeout: float = 30, reason: str = "download timed out"):
        self.timeout = timeout
        self.reason = reason
        super().__init__(f"Download failed: {reason} (timeout:{timeout}s)")


class ScreenshotError(ActionError):
    """Failed to capture screenshot."""

    def __init__(self, path: str = "", reason: str = "capture failed"):
        self.path = path
        self.reason = reason
        super().__init__(f"Screenshot failed for '{path}': {reason}")


# ---------------------------------------------------------------------------
# Config errors
# ---------------------------------------------------------------------------

class ConfigError(PyWebFlxError):
    """Invalid configuration value."""

    def __init__(self, param: str, value: object = None, reason: str = "invalid"):
        self.param = param
        self.value = value
        self.reason = reason
        super().__init__(f"Config error: {param}={value!r} — {reason}")
