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

### Via CLI

```bash
pywebflx install-extension
```

The command shows the path to the `extension/` folder and opens `chrome://extensions`.

### Manual

1. Open `chrome://extensions` in Chrome
2. Enable **Developer mode** (top right corner)
3. Click **Load unpacked**
4. Select the `extension/` folder from the project
5. The **PyWebFlx Bridge** extension should appear

## 3. Verify

```bash
pywebflx check
```

If you see "Extension is CONNECTED!", everything is ready.

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
