# PyWebFlx - Project Instructions

## Overview

PyWebFlx is a Python browser automation library that connects to already-open Chrome pages via Chrome Extension (Manifest V3) + WebSocket. The Python side runs a WebSocket server; the extension connects as a client.

## Architecture

- **Python package**: `src/pywebflx/` (async/await API)
- **Chrome Extension**: `extension/` (Manifest V3, service worker)
- **Documentation**: `docs/` (MkDocs Material, bilingual EN + PT-BR)
- **Tests**: `tests/`

## Documentation Rules

- **ALWAYS** update documentation when changing the API, adding features, or modifying behavior.
- Documentation lives in `docs/` with MkDocs Material + mkdocs-static-i18n.
- Every `.md` file has a `.pt.md` counterpart (PT-BR translation). **Always update both**.
- PT-BR docs must use proper accents (acentuacao correta).
- After updating docs, deploy with: `"C:/Program Files/Python313/python.exe" -m mkdocs gh-deploy --force`
- Do NOT mention UiPath in any documentation.

## Key Commands

```bash
# Run tests
"C:/Program Files/Python313/python.exe" -m pytest tests/ -v

# Deploy docs
"C:/Program Files/Python313/python.exe" -m mkdocs gh-deploy --force

# Install in dev mode
"C:/Program Files/Python313/python.exe" -m pip install -e ".[dev]"
```

## Conventions

- Python path on this machine: `C:/Program Files/Python313/python.exe`
- WebSocket port: 9819
- All Python code uses async/await with asyncio
- Extension uses chrome.scripting.executeScript (no eval/new Function due to CSP)
- The `open` parameter in `use_browser()` follows: `"if_not_open"` (default), `"open"`, `"never"`
- URL and title matching is partial (contains), not exact

## Git

- Remote: https://github.com/theflexa/pywebflx
- Author: Flexa <the.flexa@outlook.com>
- Docs site: https://theflexa.github.io/pywebflx/
- Main branch: `master`
