"""Tests for selector resolution (CSS, XPath, attributes)."""

import pytest
from pywebflx.selectors import resolve_selector, detect_selector_type, SelectorResult
from pywebflx.exceptions import SelectorError


class TestDetectSelectorType:
    """Verify automatic detection of selector type from string."""

    def test_css_id_selector(self):
        assert detect_selector_type("#btn-login") == "css"

    def test_css_class_selector(self):
        assert detect_selector_type(".my-class") == "css"

    def test_css_tag_selector(self):
        assert detect_selector_type("button") == "css"

    def test_css_attribute_selector(self):
        assert detect_selector_type("[data-testid='submit']") == "css"

    def test_css_complex_selector(self):
        assert detect_selector_type("div.container > ul li:first-child") == "css"

    def test_xpath_starts_with_slash(self):
        assert detect_selector_type("//button[@id='submit']") == "xpath"

    def test_xpath_starts_with_dot_slash(self):
        assert detect_selector_type(".//div[@class='item']") == "xpath"

    def test_xpath_starts_with_parenthesis(self):
        assert detect_selector_type("(//div)[1]") == "xpath"


class TestResolveSelector:
    """Verify resolve_selector builds correct JS code for each type."""

    def test_css_selector_returns_queryselector(self):
        result = resolve_selector("#btn")
        assert result.selector_type == "css"
        assert result.selector == "#btn"
        assert "querySelector" in result.js_expression

    def test_xpath_selector_returns_evaluate(self):
        result = resolve_selector("//button[@id='ok']")
        assert result.selector_type == "xpath"
        assert "evaluate" in result.js_expression

    def test_attribute_text_selector(self):
        result = resolve_selector(text="Entrar")
        assert result.selector_type == "attributes"
        assert "Entrar" in result.js_expression

    def test_attribute_text_with_tag(self):
        result = resolve_selector(text="Salvar", tag="button")
        assert result.selector_type == "attributes"
        assert "button" in result.js_expression
        assert "Salvar" in result.js_expression

    def test_attribute_role_selector(self):
        result = resolve_selector(role="button", name="Submit")
        assert result.selector_type == "attributes"
        assert "role" in result.js_expression

    def test_empty_selector_raises(self):
        with pytest.raises(SelectorError):
            resolve_selector("")

    def test_none_selector_with_no_attributes_raises(self):
        with pytest.raises(SelectorError):
            resolve_selector(None)
