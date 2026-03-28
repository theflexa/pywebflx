# Exceptions

All exceptions inherit from `PyWebFlxError` and carry contextual attributes.

## Hierarchy

```
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
```

## Contextual attributes

Each exception carries relevant information for debugging:

```python
try:
    await browser.click("#nonexistent-btn")
except ElementNotFoundError as e:
    print(e.selector)   # "#nonexistent-btn"
    print(e.tab_id)     # 42
    print(e.timeout)    # 10
    print(e.message)    # "Element '#nonexistent-btn' not found within 10s"
```

## Reference

### Connection

| Exception | When | Attributes |
|-----------|------|------------|
| `ExtensionNotConnectedError` | Extension did not connect in time | `port`, `timeout` |
| `ConnectionLostError` | WebSocket dropped during operation | `reason` |

### Browser

| Exception | When | Attributes |
|-----------|------|------------|
| `BrowserNotFoundError` | No tab found | `title`, `url` |
| `TabNotFoundError` | Specific tab not found | `title`, `url` |
| `TabClosedError` | Tab closed during operation | `tab_id` |

### Element

| Exception | When | Attributes |
|-----------|------|------------|
| `ElementNotFoundError` | Selector did not find element | `selector`, `tab_id`, `timeout` |
| `ElementTimeoutError` | Timeout waiting for condition | `selector`, `tab_id`, `timeout`, `condition` |
| `ElementNotInteractableError` | Element not clickable | `selector`, `tab_id`, `reason` |
| `SelectorError` | Invalid selector | `selector`, `reason` |

### Action

| Exception | When | Attributes |
|-----------|------|------------|
| `NavigationError` | Failed to navigate | `url`, `reason` |
| `InjectionError` | Failed to inject script | `tab_id`, `reason` |
| `DownloadError` | Download failed/timeout | `timeout`, `reason` |
| `ScreenshotError` | Screenshot failed | `path`, `reason` |

### Config

| Exception | When | Attributes |
|-----------|------|------------|
| `ConfigError` | Invalid config value | `param`, `value`, `reason` |

## Full example

```python
from pywebflx import use_browser, BrowserNotFoundError, ElementNotFoundError

try:
    async with use_browser(url="portal.com", open="never") as browser:
        try:
            await browser.click("#btn-login", timeout=5)
        except ElementNotFoundError as e:
            print(f"Button {e.selector} not found in tab {e.tab_id}")
except BrowserNotFoundError as e:
    print(f"No tab with url={e.url}")
```
