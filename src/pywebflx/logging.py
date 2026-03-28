"""PyWebFlx structured logging system.

Provides:
- configure_logging(): Set up log level, sink, format
- @_logged_action: Decorator that auto-logs every browser action with
  timestamp, action name, selector, tab, duration, retries, and errors.

Log format:
    2026-03-28 14:32:05.123 [INFO]  [browser.click] #btn -> tab:42 -> success (120ms)
"""

from __future__ import annotations

import functools
import time
from typing import Any, Callable

try:
    from loguru import logger

    _LOGURU_AVAILABLE = True
except ImportError:
    import logging

    logger = logging.getLogger("pywebflx")
    _LOGURU_AVAILABLE = False

_timestamp_format: str = "%Y-%m-%d %H:%M:%S.%f"


def configure_logging(
    level: str = "INFO",
    sink: str | None = None,
    handler: Any = None,
    timestamp_format: str | None = None,
) -> None:
    """Configure PyWebFlx logging output.

    Args:
        level: Log level -- TRACE, DEBUG, INFO, WARN, ERROR, or DISABLED.
        sink: File path to write logs to. If None, logs to stderr.
        handler: Custom log handler (loguru sink or logging.Handler).
        timestamp_format: strftime format for timestamps.
    """
    global _timestamp_format
    if timestamp_format is not None:
        _timestamp_format = timestamp_format

    if _LOGURU_AVAILABLE:
        logger.remove()
        if level.upper() == "DISABLED":
            return
        fmt = "{time:" + _timestamp_format.replace("%Y", "YYYY").replace(
            "%m", "MM"
        ).replace("%d", "DD").replace("%H", "HH").replace("%M", "mm").replace(
            "%S", "ss"
        ).replace("%f", "SSS") + "} [{level}] {message}"

        if handler is not None:
            logger.add(handler, level=level.upper(), format=fmt)
        elif sink is not None:
            logger.add(sink, level=level.upper(), format=fmt)
        else:
            logger.add(
                lambda msg: print(msg, end=""),
                level=level.upper(),
                format=fmt,
                colorize=True,
            )
    else:
        log = logging.getLogger("pywebflx")
        log.handlers.clear()
        if level.upper() == "DISABLED":
            log.addHandler(logging.NullHandler())
            return
        log.setLevel(getattr(logging, level.upper(), logging.INFO))
        if handler is not None:
            log.addHandler(handler)
        elif sink is not None:
            log.addHandler(logging.FileHandler(sink))
        else:
            sh = logging.StreamHandler()
            sh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
            log.addHandler(sh)


def _format_log_message(
    action: str,
    selector: str = "",
    tab_id: int | None = None,
    status: str = "success",
    duration_ms: float | None = None,
    attempt: int | None = None,
    max_attempts: int | None = None,
    error_name: str | None = None,
    extra: str | None = None,
) -> str:
    """Format a structured log message for a browser action."""
    parts = [f"[{action}]"]

    if selector:
        parts.append(selector)

    if extra:
        parts.append(f"-> {extra}")

    if tab_id is not None:
        parts.append(f"-> tab:{tab_id}")

    if status == "retry":
        retry_info = f"retry {attempt}/{max_attempts}" if max_attempts else f"retry {attempt}"
        parts.append(f"-> {retry_info}")
        if error_name:
            parts.append(f"({error_name})")
    elif status == "failed":
        parts.append("-> failed")
        if error_name:
            parts.append(f": {error_name}")
    elif status == "success":
        if attempt and attempt > 1:
            parts.append(f"-> success (retry {attempt}")
            if duration_ms is not None:
                parts[-1] = parts[-1] + f", {duration_ms:.0f}ms)"
            else:
                parts[-1] = parts[-1] + ")"
        else:
            if duration_ms is not None:
                parts.append(f"-> success ({duration_ms:.0f}ms)")
            else:
                parts.append("-> success")

    return " ".join(parts)


def _logged_action(action_name: str) -> Callable:
    """Decorator that adds structured logging to async browser action methods."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, selector: str = "", **kwargs):
            log_level = kwargs.pop("log_level", None)
            if log_level is None and hasattr(self, "_config"):
                log_level = self._config.resolve("log_level", None)
            if log_level is None:
                log_level = "INFO"

            tab_id = getattr(self, "_tab_id", None)
            start = time.perf_counter()

            try:
                result = await func(self, selector, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                msg = _format_log_message(
                    action=action_name,
                    selector=str(selector),
                    tab_id=tab_id,
                    status="success",
                    duration_ms=duration_ms,
                )
                _log(log_level, msg)
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                msg = _format_log_message(
                    action=action_name,
                    selector=str(selector),
                    tab_id=tab_id,
                    status="failed",
                    error_name=type(e).__name__,
                )
                _log("ERROR", msg)
                raise

        return wrapper

    return decorator


def _log(level: str, message: str) -> None:
    """Route a message to the active logger at the given level."""
    level = level.upper()
    if _LOGURU_AVAILABLE:
        logger.opt(depth=2).log(level, message)
    else:
        log = logging.getLogger("pywebflx")
        py_level = getattr(logging, level if level != "TRACE" else "DEBUG", logging.INFO)
        log.log(py_level, message)
