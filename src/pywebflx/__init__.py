"""PyWebFlx — Browser automation for already-open Chrome pages.

Example:
    from pywebflx import use_browser, PyWebFlxConfig, configure_logging

    configure_logging(level="INFO")

    async with use_browser(url="sicoob.com.br") as browser:
        await browser.click("#btn-login")
        text = await browser.get_text(".welcome")
"""

__version__ = "0.1.3"

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
