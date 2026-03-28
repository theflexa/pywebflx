"""Tests for PyWebFlxConfig."""

import pytest
from pywebflx.config import PyWebFlxConfig
from pywebflx.exceptions import ConfigError


class TestPyWebFlxConfigDefaults:
    """Verify default configuration values."""

    def test_default_timeout(self):
        config = PyWebFlxConfig()
        assert config.default_timeout == 10

    def test_default_delay_between_actions(self):
        config = PyWebFlxConfig()
        assert config.delay_between_actions == 0.3

    def test_default_retry_count(self):
        config = PyWebFlxConfig()
        assert config.retry_count == 0

    def test_default_on_error(self):
        config = PyWebFlxConfig()
        assert config.on_error == "raise"

    def test_default_ws_port(self):
        config = PyWebFlxConfig()
        assert config.ws_port == 9819

    def test_default_log_level(self):
        config = PyWebFlxConfig()
        assert config.log_level == "INFO"


class TestPyWebFlxConfigCustom:
    """Verify custom configuration values."""

    def test_custom_values(self):
        config = PyWebFlxConfig(
            default_timeout=30,
            delay_between_actions=0.5,
            retry_count=3,
            on_error="continue",
            ws_port=8080,
            log_level="DEBUG",
        )
        assert config.default_timeout == 30
        assert config.delay_between_actions == 0.5
        assert config.retry_count == 3
        assert config.on_error == "continue"
        assert config.ws_port == 8080
        assert config.log_level == "DEBUG"

    def test_invalid_on_error_raises(self):
        with pytest.raises(ConfigError) as exc_info:
            PyWebFlxConfig(on_error="ignore")
        assert exc_info.value.param == "on_error"

    def test_invalid_timeout_raises(self):
        with pytest.raises(ConfigError):
            PyWebFlxConfig(default_timeout=-1)

    def test_invalid_ws_port_raises(self):
        with pytest.raises(ConfigError):
            PyWebFlxConfig(ws_port=0)

    def test_invalid_log_level_raises(self):
        with pytest.raises(ConfigError):
            PyWebFlxConfig(log_level="SUPERVERBOSE")


class TestPyWebFlxConfigGlobalDefaults:
    """Verify global defaults mechanism."""

    def setup_method(self):
        PyWebFlxConfig.reset_defaults()

    def teardown_method(self):
        PyWebFlxConfig.reset_defaults()

    def test_set_defaults_affects_new_instances(self):
        PyWebFlxConfig.set_defaults(default_timeout=20, retry_count=5)
        config = PyWebFlxConfig()
        assert config.default_timeout == 20
        assert config.retry_count == 5

    def test_explicit_params_override_global_defaults(self):
        PyWebFlxConfig.set_defaults(default_timeout=20)
        config = PyWebFlxConfig(default_timeout=5)
        assert config.default_timeout == 5

    def test_reset_defaults(self):
        PyWebFlxConfig.set_defaults(default_timeout=99)
        PyWebFlxConfig.reset_defaults()
        config = PyWebFlxConfig()
        assert config.default_timeout == 10


class TestPyWebFlxConfigResolve:
    """Verify parameter priority resolution: action > config > global."""

    def test_resolve_returns_action_param_when_provided(self):
        config = PyWebFlxConfig(default_timeout=10)
        assert config.resolve("timeout", action_value=30) == 30

    def test_resolve_returns_config_when_no_action_param(self):
        config = PyWebFlxConfig(default_timeout=10)
        assert config.resolve("timeout", action_value=None) == 10

    def test_resolve_returns_global_default_for_unset_config(self):
        PyWebFlxConfig.set_defaults(default_timeout=20)
        config = PyWebFlxConfig()
        assert config.resolve("timeout", action_value=None) == 20
        PyWebFlxConfig.reset_defaults()
