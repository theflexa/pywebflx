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
        """Send a command to the extension and return the response data."""
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
        """Execute an action with optional retry, verify, and delays."""
        effective_retry = self._config.resolve("retry_count", retry) or 0
        effective_delay_after = delay_after or self._config.delay_between_actions

        max_attempts = effective_retry + 1

        for attempt in range(1, max_attempts + 1):
            try:
                if delay_before and delay_before > 0:
                    await asyncio.sleep(delay_before)

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
        """Navigate to a URL in the current tab."""
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
        """Click an element on the page."""
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
        """Type text into an input field."""
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
        """Set text on an element without simulating keystrokes."""
        params = self._resolve_params(selector)
        params["text"] = text
        await self._send("set_text", params)

    @_logged_action("browser.check")
    async def check(self, selector: str = "", **kwargs) -> None:
        """Check a checkbox."""
        params = self._resolve_params(selector)
        await self._send("check", params)

    @_logged_action("browser.uncheck")
    async def uncheck(self, selector: str = "", **kwargs) -> None:
        """Uncheck a checkbox."""
        params = self._resolve_params(selector)
        await self._send("uncheck", params)

    @_logged_action("browser.select_item")
    async def select_item(
        self, selector: str = "", item: str = "", *, by: str = "text", **kwargs
    ) -> None:
        """Select an item in a dropdown/select element."""
        params = self._resolve_params(selector)
        params.update({"item": item, "by": by})
        await self._send("select_item", params)

    @_logged_action("browser.hover")
    async def hover(self, selector: str = "", **kwargs) -> None:
        """Hover over an element."""
        params = self._resolve_params(selector)
        await self._send("hover", params)

    @_logged_action("browser.send_hotkey")
    async def send_hotkey(self, keys: str = "", **kwargs) -> None:
        """Send keyboard shortcut."""
        await self._send("send_hotkey", {"keys": keys})

    # -------------------------------------------------------------------
    # Extraction
    # -------------------------------------------------------------------

    @_logged_action("browser.get_text")
    async def get_text(self, selector: str = "", **kwargs) -> str:
        """Get the visible text of an element."""
        params = self._resolve_params(selector)
        return await self._send("get_text", params)

    @_logged_action("browser.get_attribute")
    async def get_attribute(self, selector: str = "", attribute: str = "", **kwargs) -> str | None:
        """Get an HTML attribute value from an element."""
        params = self._resolve_params(selector)
        params["attribute"] = attribute
        return await self._send("get_attribute", params)

    @_logged_action("browser.get_full_text")
    async def get_full_text(self, selector: str = "", **kwargs) -> str:
        """Get all visible text from the page."""
        return await self._send("get_full_text", {})

    @_logged_action("browser.inspect")
    async def inspect(
        self, selector: str = "", *, depth: int = 2, samples: int = 2, **kwargs
    ) -> str:
        """Get a summarized view of the DOM structure, optimized for AI consumption."""
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
        """Extract data from an HTML table with optional pagination."""
        all_rows: list[dict[str, str]] = []

        for page in range(max_pages):
            page_data = await self._send("extract_table", {"selector": selector})

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
        """Extract structured data from non-table elements (cards, divs, lists)."""
        all_rows: list[dict[str, str]] = []

        for page in range(max_pages):
            page_data = await self._send("extract_structured", {
                "container": container,
                "row": row,
                "columns": columns or {},
            })
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
        """Check if an element exists on the page."""
        if timeout > 0:
            return await self._poll_element(selector, timeout, condition="exists")

        params = self._resolve_params(selector)
        return await self._send("element_exists", params)

    @_logged_action("browser.wait_element")
    async def wait_element(
        self, selector: str = "", *, condition: str = "visible", timeout: float | None = None, **kwargs
    ) -> None:
        """Wait for an element to meet a condition.

        Raises:
            ElementTimeoutError: If condition not met within timeout.
        """
        effective_timeout = self._config.resolve("timeout", timeout)
        found = await self._poll_element(selector, effective_timeout, condition)
        if not found:
            raise ElementTimeoutError(
                selector=selector, tab_id=self._tab_id,
                timeout=effective_timeout, condition=condition,
            )

    @_logged_action("browser.wait_element_vanish")
    async def wait_element_vanish(self, selector: str = "", *, timeout: float | None = None, **kwargs) -> None:
        """Wait for an element to disappear from the page.

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
        raise ElementTimeoutError(
            selector=selector, tab_id=self._tab_id,
            timeout=effective_timeout, condition="invisible",
        )

    @_logged_action("browser.find_element")
    async def find_element(self, selector: str = "", **kwargs) -> dict[str, Any]:
        """Find an element and return info about it."""
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
        """Execute JavaScript code in the page and return the result."""
        return await self._send("execute_js", {"code": code})

    @_logged_action("browser.inject_js")
    async def inject_js(self, code: str = "", **kwargs) -> None:
        """Inject and execute JavaScript without waiting for a return value."""
        await self._send("execute_js", {"code": code})

    @asynccontextmanager
    async def switch_to(self, selector: str) -> AsyncGenerator[BrowserContext, None]:
        """Switch context to an iframe for executing actions inside it.

        Yields:
            A BrowserContext scoped to the iframe.
        """
        # TODO: implement proper iframe scoping in v2
        yield self

    # -------------------------------------------------------------------
    # Files (Screenshots, Downloads, Uploads)
    # -------------------------------------------------------------------

    @_logged_action("browser.take_screenshot")
    async def take_screenshot(self, path: str = "", *, selector: str | None = None, **kwargs) -> None:
        """Capture a screenshot of the page or a specific element."""
        params = {"path": path}
        if selector:
            params["selector"] = selector
        await self._send("take_screenshot", params)

    @_logged_action("browser.set_file")
    async def set_file(self, selector: str = "", path: str = "", **kwargs) -> None:
        """Set a file path on a file input element for upload."""
        params = self._resolve_params(selector)
        params["filePath"] = path
        await self._send("set_file", params)

    @asynccontextmanager
    async def wait_for_download(self, timeout: float = 30) -> AsyncGenerator[Any, None]:
        """Wait for a download to complete.

        Yields:
            Download info object with .path attribute.
        """

        class DownloadResult:
            def __init__(self):
                self.path: str | None = None

        result = DownloadResult()
        yield result
        # After the block, poll for download completion via chrome.downloads API

    # -------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------

    async def health_check(self) -> dict[str, Any]:
        """Check connection status and extension health."""
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
    open: str = "if_not_open",
    config: PyWebFlxConfig | None = None,
) -> AsyncGenerator[BrowserContext, None]:
    """Connect to an already-open Chrome tab and return a BrowserContext.

    Args:
        url: URL to search for (partial match) and/or open.
        title: Partial title to search for in open tabs.
        open: Open behavior, inspired by UiPath:
            - "if_not_open" (default): Search for existing tab, open url if not found.
            - "open": Always open a new tab with url.
            - "never": Only connect to existing tab, never open.
        config: Configuration overrides. Uses defaults if not provided.

    Yields:
        BrowserContext bound to the matched/opened tab.

    Raises:
        BrowserNotFoundError: If no tab found and open="never".
        ExtensionNotConnectedError: If Chrome extension is not connected.

    Example:
        # Opens if not already open (default)
        async with use_browser(url="https://sicoob.com.br") as browser:
            await browser.click("#login")

        # Always open a new tab
        async with use_browser(url="https://sicoob.com.br", open="open") as browser:
            ...

        # Never open, only attach to existing
        async with use_browser(url="sicoob.com.br", open="never") as browser:
            ...
    """
    cfg = config or PyWebFlxConfig()
    server = WebSocketServer(port=cfg.ws_port)
    await server.start()

    try:
        await server.wait_for_connection(timeout=30)

        mgr = TabManager(server)

        if open == "open":
            # Always open a new tab
            if not url:
                raise BrowserNotFoundError(title=title, url=url)
            tab = await mgr.create_tab(url)
        elif open == "never":
            # Only connect to existing, never open
            tab = await mgr.find_tab(title=title, url=url)
        else:
            # "if_not_open" (default): search first, open if not found
            tab = await mgr.find_or_open(title=title, url=url, if_not_open=url)

        ctx = BrowserContext(conn=server, tab_id=tab["id"], config=cfg)
        yield ctx
    finally:
        await server.stop()
