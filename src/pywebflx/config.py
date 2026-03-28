"""PyWebFlx configuration management.

Handles default values, custom configuration, and parameter priority
resolution (action param > instance config > global defaults).

Example:
    config = PyWebFlxConfig(default_timeout=15, retry_count=3)

    async with use_browser(url="example.com", config=config) as browser:
        await browser.click("#btn", timeout=30)  # 30 wins over 15

    # Global defaults affect all new instances:
    PyWebFlxConfig.set_defaults(default_timeout=20)
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from pywebflx.exceptions import ConfigError

_VALID_ON_ERROR = ("raise", "continue")
_VALID_LOG_LEVELS = ("TRACE", "DEBUG", "INFO", "WARN", "WARNING", "ERROR", "DISABLED")

_BUILTIN_DEFAULTS: dict[str, Any] = {
    "default_timeout": 10,
    "delay_between_actions": 0.3,
    "retry_count": 0,
    "on_error": "raise",
    "ws_port": 9819,
    "log_level": "INFO",
}

_global_defaults: dict[str, Any] = {}

# Maps resolve() short names to config field names
_RESOLVE_ALIASES: dict[str, str] = {
    "timeout": "default_timeout",
}


def _validate(
    default_timeout: float,
    delay_between_actions: float,
    retry_count: int,
    on_error: str,
    ws_port: int,
    log_level: str,
) -> None:
    if default_timeout < 0:
        raise ConfigError("default_timeout", default_timeout, "must be >= 0")
    if delay_between_actions < 0:
        raise ConfigError("delay_between_actions", delay_between_actions, "must be >= 0")
    if retry_count < 0:
        raise ConfigError("retry_count", retry_count, "must be >= 0")
    if on_error not in _VALID_ON_ERROR:
        raise ConfigError("on_error", on_error, f"must be one of {_VALID_ON_ERROR}")
    if not (1 <= ws_port <= 65535):
        raise ConfigError("ws_port", ws_port, "must be between 1 and 65535")
    if log_level.upper() not in _VALID_LOG_LEVELS:
        raise ConfigError("log_level", log_level, f"must be one of {_VALID_LOG_LEVELS}")


@dataclass
class PyWebFlxConfig:
    """Configuration for PyWebFlx browser sessions."""

    default_timeout: float = None
    delay_between_actions: float = None
    retry_count: int = None
    on_error: str = None
    ws_port: int = None
    log_level: str = None

    def __post_init__(self):
        for f in fields(self):
            if getattr(self, f.name) is None:
                value = _global_defaults.get(f.name, _BUILTIN_DEFAULTS[f.name])
                object.__setattr__(self, f.name, value)

        _validate(
            self.default_timeout,
            self.delay_between_actions,
            self.retry_count,
            self.on_error,
            self.ws_port,
            self.log_level,
        )

    def resolve(self, param_name: str, action_value: Any) -> Any:
        """Resolve a parameter value with priority: action > config > global."""
        if action_value is not None:
            return action_value
        field_name = _RESOLVE_ALIASES.get(param_name, param_name)
        return getattr(self, field_name, None)

    @staticmethod
    def set_defaults(**kwargs: Any) -> None:
        """Set global defaults that affect all new PyWebFlxConfig instances."""
        valid_fields = {f.name for f in fields(PyWebFlxConfig)}
        for key in kwargs:
            if key not in valid_fields:
                raise ConfigError(key, kwargs[key], "unknown config field")
        _global_defaults.update(kwargs)

    @staticmethod
    def reset_defaults() -> None:
        """Reset global defaults to builtin values."""
        _global_defaults.clear()
