# PyWebFlx

**Browser automation for already-open Chrome pages.**

PyWebFlx is a Python library that connects to pages already open in Chrome via an extension (Manifest V3) + WebSocket. Unlike Selenium, it does not create a sandbox instance -- you automate the user's real browser.

---

## Quick Start

```python
import asyncio
from pywebflx import use_browser

async def main():
    async with use_browser(url="https://quotes.toscrape.com/") as browser:
        # View page structure
        structure = await browser.inspect(depth=5)
        print(structure)

        # Extract data
        quotes = await browser.extract_data(
            container="body",
            row=".quote",
            columns={"text": ".text", "author": ".author"}
        )
        for q in quotes:
            print(f"{q['author']}: {q['text'][:60]}...")

asyncio.run(main())
```

## Why PyWebFlx?

| | PyWebFlx | Selenium | Playwright |
|---|---|---|---|
| Uses already-open Chrome | :white_check_mark: | :x: | :x: |
| Reuses session/login | :white_check_mark: | :x: | :x: |
| Async/await API | :white_check_mark: | :x: | :white_check_mark: |
| No WebDriver/binary | :white_check_mark: | :x: | :x: |
| AI-optimized inspect | :white_check_mark: | :x: | :x: |
| Setup | Chrome Extension | WebDriver + config | `playwright install` |

## How it works

```
Python Script                   Chrome Extension
      |                                |
      |  1. Starts WebSocket :9819     |
      |<------------------------------>|  2. Connects automatically
      |                                |
      |  3. JSON command               |
      |------------------------------->|  4. Injects script into tab
      |                                |     via chrome.scripting
      |  5. JSON result                |
      |<-------------------------------|
      |                                |
```

## Main features

- **`use_browser()`** -- Connects to tabs by URL or title, opens if not found
- **`click()`, `type_into()`** -- Element interaction (CSS, XPath, text)
- **`get_text()`, `extract_data()`** -- Structured data extraction
- **`inspect()`** -- Summarized DOM view, optimized for AIs
- **`extract_table()`** -- HTML table extraction with pagination
- **`wait_element()`, `element_exists()`** -- Synchronization
- **`execute_js()`** -- Custom JavaScript
