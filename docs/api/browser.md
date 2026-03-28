# use_browser

Main entry point for PyWebFlx. Connects to a Chrome tab and returns a `BrowserContext` with all automation methods.

## Signature

```python
async with use_browser(
    url: str = None,
    title: str = None,
    open: str = "if_not_open",
    config: PyWebFlxConfig = None,
) as browser:
    ...
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | `None` | URL to search (partial match) and/or open |
| `title` | `str` | `None` | Tab title to search (partial match) |
| `open` | `str` | `"if_not_open"` | Opening behavior (see below) |
| `config` | `PyWebFlxConfig` | `None` | Custom configuration |

!!! info "Partial match"
    Both `url` and `title` use **partial match** (contains). You don't need the full URL — just the fixed part is enough. This is especially useful for dynamic URLs:

    ```python
    # Matches any tab at mycon.gupy.io/candidates/...
    async with use_browser(url="mycon.gupy.io/candidates") as browser:
        ...
    ```

!!! tip "Combining `url` and `title`"
    You can use both parameters together. The search uses **AND** logic — the tab must match both criteria:

    ```python
    # Tab must contain "gupy.io" in URL AND "Candidatos" in title
    async with use_browser(url="gupy.io", title="Candidatos") as browser:
        ...
    ```

### `open` parameter

| Value | Behavior |
|-------|----------|
| `"if_not_open"` | Searches for an existing tab. If not found, opens the `url`. **(default)** |
| `"open"` | Always opens a new tab with the `url`. |
| `"never"` | Only connects to an existing tab. Never opens. |

## Examples

### Basic -- opens if not found

```python
async with use_browser(url="https://quotes.toscrape.com/") as browser:
    await browser.click("#btn")
```

### Search by title

```python
async with use_browser(title="Portal Sicoob", open="never") as browser:
    balance = await browser.get_text(".balance")
```

### Always open a new tab

```python
async with use_browser(url="https://example.com", open="open") as browser:
    await browser.type_into("#email", text="user@email.com")
```

### With custom configuration

```python
from pywebflx import PyWebFlxConfig

config = PyWebFlxConfig(default_timeout=30, retry_count=3)

async with use_browser(url="https://example.com", config=config) as browser:
    await browser.click("#btn", timeout=60)  # 60 overrides 30
```

### Multiple tabs

```python
async with use_browser(url="https://portal.com") as tab1:
    async with use_browser(url="https://email.com") as tab2:
        data = await tab1.get_text(".balance")
        await tab2.type_into("#body", text=data)
```

## Exceptions

| Exception | When |
|-----------|------|
| `BrowserNotFoundError` | Tab not found and `open="never"` |
| `ExtensionNotConnectedError` | Chrome extension is not connected |
