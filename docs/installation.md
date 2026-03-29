# Installation

## 1. Install the library

```bash
pip install pywebflx
```

Or for development:

```bash
git clone https://github.com/theflexa/pywebflx.git
cd pywebflx
pip install -e ".[dev]"
```

## 2. Install the Chrome extension

```bash
pywebflx install-extension
```

The command will show the **extension path**. Then:

1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer mode** (toggle in the top-right corner)
3. Click **Load unpacked**
4. Paste the path shown by the command and confirm

!!! tip "Enterprise setup (multiple machines)"
    The same steps apply for each machine. After `pip install pywebflx`, the extension is bundled inside the package — no additional downloads needed.

## 3. Verify

```bash
pywebflx check
```

If you see "Extension is CONNECTED!", everything is ready.

## CLI commands

| Command | Description |
|---------|-------------|
| `pywebflx install-extension` | Shows the extension path for installation |
| `pywebflx check` | Verify extension connection |
| `pywebflx uninstall-extension` | Instructions to remove the extension |
| `pywebflx extension-path` | Print extension path (useful for scripts) |
| `pywebflx --version` | Show installed version |

## Requirements

- Python 3.10+
- Google Chrome
- PyWebFlx Bridge extension installed

## Dependencies

| Package | Usage |
|---------|-------|
| `websockets` | Python <-> Extension communication |
| `loguru` | Structured logging |
| `click` | CLI (install-extension, check) |
