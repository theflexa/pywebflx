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
