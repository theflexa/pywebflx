"""Selector resolution for PyWebFlx.

Converts CSS selectors, XPath expressions, or humanized attribute queries
into JavaScript expressions that can be injected into Chrome tabs.

Supports three selector types:
- CSS: "#btn", ".class", "div > span"
- XPath: "//button[@id='ok']", ".//div"
- Attributes: text="Entrar", tag="button", role="button", name="Submit"
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from pywebflx.exceptions import SelectorError


@dataclass
class SelectorResult:
    """Result of resolving a selector.

    Attributes:
        selector: The original selector string or description.
        selector_type: One of "css", "xpath", "attributes".
        js_expression: JavaScript code that locates the element in the DOM.
    """

    selector: str
    selector_type: str
    js_expression: str


def detect_selector_type(selector: str) -> str:
    """Detect whether a string selector is CSS or XPath.

    Rules:
        - Starts with "/", "./" or "(" -> XPath
        - Everything else -> CSS
    """
    stripped = selector.strip()
    if stripped.startswith(("//", "./", "(/")):
        return "xpath"
    if stripped.startswith(".//"):
        return "xpath"
    return "css"


def resolve_selector(
    selector: str | None = None,
    *,
    text: str | None = None,
    tag: str | None = None,
    role: str | None = None,
    name: str | None = None,
) -> SelectorResult:
    """Resolve a selector into a JavaScript expression for DOM lookup.

    Can be called with a CSS/XPath string selector, or with keyword
    arguments for attribute-based lookup.

    Raises:
        SelectorError: If no valid selector or attributes provided.
    """
    has_attributes = any(v is not None for v in (text, tag, role, name))

    if selector and isinstance(selector, str) and selector.strip():
        sel_type = detect_selector_type(selector)
        if sel_type == "css":
            js = f"document.querySelector({json.dumps(selector)})"
            return SelectorResult(
                selector=selector,
                selector_type="css",
                js_expression=js,
            )
        else:
            js = (
                f"document.evaluate({json.dumps(selector)}, document, null, "
                f"XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue"
            )
            return SelectorResult(
                selector=selector,
                selector_type="xpath",
                js_expression=js,
            )

    if has_attributes:
        return _resolve_attributes(text=text, tag=tag, role=role, name=name)

    raise SelectorError(
        selector=str(selector),
        reason="No valid selector or attributes provided",
    )


def _resolve_attributes(
    text: str | None = None,
    tag: str | None = None,
    role: str | None = None,
    name: str | None = None,
) -> SelectorResult:
    """Build a JS expression that finds an element by attributes."""
    description_parts = []
    filters = []
    base_selector = tag or "*"

    if role:
        base_selector = f'{tag or "*"}[role={json.dumps(role)}]'
        description_parts.append(f"role={role}")

    if name:
        filters.append(
            f'(el.getAttribute("aria-label") === {json.dumps(name)} || '
            f'el.getAttribute("name") === {json.dumps(name)})'
        )
        description_parts.append(f"name={name}")

    if text:
        filters.append(
            f"el.textContent.trim() === {json.dumps(text)}"
        )
        description_parts.append(f"text={text}")

    if tag:
        description_parts.insert(0, f"tag={tag}")

    description = ", ".join(description_parts)

    if filters:
        filter_expr = " && ".join(filters)
        js = (
            f"Array.from(document.querySelectorAll({json.dumps(base_selector)}))"
            f".find(el => {filter_expr})"
        )
    else:
        js = f"document.querySelector({json.dumps(base_selector)})"

    return SelectorResult(
        selector=f"[{description}]",
        selector_type="attributes",
        js_expression=js,
    )
