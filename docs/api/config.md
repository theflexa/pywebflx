# Configuration

`PyWebFlxConfig` controls timeouts, retries, WebSocket port, and logging.

## Signature

```python
from pywebflx import PyWebFlxConfig

config = PyWebFlxConfig(
    default_timeout=10,
    delay_between_actions=0.3,
    retry_count=0,
    on_error="raise",
    ws_port=9819,
    log_level="INFO",
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `default_timeout` | `float` | `10` | Default timeout in seconds |
| `delay_between_actions` | `float` | `0.3` | Delay between consecutive actions |
| `retry_count` | `int` | `0` | Default retry attempts on failure |
| `on_error` | `str` | `"raise"` | `"raise"` or `"continue"` |
| `ws_port` | `int` | `9819` | WebSocket server port |
| `log_level` | `str` | `"INFO"` | Log level |

## Priority

Parameter resolution follows this order:

```
action parameter  >  use_browser config  >  global defaults
```

```python
# Global: timeout = 10 (default)
# Config: timeout = 20
# Action: timeout = 60 (wins)

config = PyWebFlxConfig(default_timeout=20)

async with use_browser(url="https://example.com", config=config) as browser:
    await browser.click("#btn", timeout=60)  # uses 60
    await browser.click("#btn2")             # uses 20
```

## Global defaults

```python
# Affect all new instances
PyWebFlxConfig.set_defaults(default_timeout=15, retry_count=3)

# Reset to original values
PyWebFlxConfig.reset_defaults()
```

## Logging

```python
from pywebflx import configure_logging

configure_logging(level="INFO")                        # console (default)
configure_logging(level="DEBUG", sink="automation.log") # file
configure_logging(level="DISABLED")                    # silent
```

### Levels

| Level | What it logs |
|-------|-------------|
| `ERROR` | Final failure (after all retries) |
| `WARN` | Retry, reconnection, fallback |
| `INFO` | Action executed successfully |
| `DEBUG` | Internal details (selector, JSON payload) |
| `TRACE` | Everything (WebSocket bytes, partial DOM) |
| `DISABLED` | Nothing |

### Format

```
2026-03-28 14:32:05.123 [INFO]  [browser.click] #btn-save -> tab:42 -> success (120ms)
2026-03-28 14:32:06.102 [WARN]  [browser.click] #btn-send -> tab:42 -> retry 1/3
2026-03-28 14:32:08.001 [ERROR] [browser.extract_table] #table -> tab:42 -> failed: TabClosedError
```

### Per-action override

```python
await browser.click("#critical-btn", log_level="DEBUG")   # more detail
await browser.click(row_selector, log_level="WARN")       # less noise in loops
```
