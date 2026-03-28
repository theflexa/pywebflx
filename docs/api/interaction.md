# Interaction

Methods for interacting with elements on the page: click, type, select, etc.

---

## click

Clicks on an element.

```python
await browser.click(selector, **kwargs)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `selector` | `str` | -- | CSS selector or XPath |
| `text` | `str` | `None` | Search by visible text |
| `tag` | `str` | `None` | Filter by HTML tag |
| `role` | `str` | `None` | Search by ARIA role |
| `name` | `str` | `None` | Search by ARIA label/name |
| `click_type` | `str` | `"single"` | `"single"` or `"double"` |
| `mouse_button` | `str` | `"left"` | `"left"`, `"right"`, `"middle"` |
| `timeout` | `float` | config | Timeout in seconds |
| `retry` | `int` | config | Retry attempts on failure |
| `verify` | `str` | `None` | Selector to verify after click |
| `delay_before` | `float` | `None` | Delay before click |
| `delay_after` | `float` | config | Delay after click |

### Examples

```python
# CSS selector
await browser.click("#btn-login")

# XPath
await browser.click("//button[@id='submit']")

# By text
await browser.click(text="Sign In", tag="button")

# Double click
await browser.click("#item", click_type="double")

# Right click
await browser.click("#menu", mouse_button="right")

# With retry and verification
await browser.click("#btn", retry=3, verify=".success", timeout=10)
```

---

## type_into

Types text into a field, simulating keystrokes.

```python
await browser.type_into(selector, text="value")
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `selector` | `str` | -- | Field selector |
| `text` | `str` | `""` | Text to type |
| `clear_before` | `bool` | `True` | Clear field before typing |
| `click_before` | `bool` | `True` | Focus/click on field before typing |
| `delay_between_keys` | `float` | `0` | Delay between keys (0 = instant) |
| `timeout` | `float` | config | Timeout |
| `retry` | `int` | config | Retry attempts |

### Examples

```python
await browser.type_into("#email", text="user@email.com")
await browser.type_into("#password", text="123456", delay_between_keys=0.05)
await browser.type_into("#field", text="append", clear_before=False)
```

---

## set_text

Sets the value of a field directly, without simulating keystrokes.

```python
await browser.set_text(selector, text="value")
```

### Example

```python
await browser.set_text("#hidden-field", text="direct-value")
```

---

## check / uncheck

Checks or unchecks a checkbox.

```python
await browser.check(selector)
await browser.uncheck(selector)
```

### Example

```python
await browser.check("#accept-terms")
await browser.uncheck("#newsletter")
```

---

## select_item

Selects an item in a `<select>` dropdown.

```python
await browser.select_item(selector, item="value", by="text")
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `selector` | `str` | -- | `<select>` selector |
| `item` | `str` | `""` | Value, text, or index to select |
| `by` | `str` | `"text"` | `"text"`, `"value"`, or `"index"` |

### Example

```python
await browser.select_item("#state", "California", by="text")
await browser.select_item("#country", "US", by="value")
await browser.select_item("#month", "0", by="index")
```

---

## hover

Hovers the mouse over an element.

```python
await browser.hover(selector)
```

### Example

```python
await browser.hover("#dropdown-menu")
```

---

## send_hotkey

Sends a keyboard shortcut.

```python
await browser.send_hotkey(keys)
```

### Examples

```python
await browser.send_hotkey("ctrl+a")
await browser.send_hotkey("Enter")
await browser.send_hotkey("ctrl+shift+s")
```

---

## Selectors

All methods accept 3 types of selectors:

| Type | Example | Detection |
|------|---------|-----------|
| CSS | `"#btn"`, `".class"`, `"div > span"` | Default |
| XPath | `"//button[@id='ok']"`, `.//div` | Starts with `//`, `./`, or `(` |
| Attributes | `text="Sign In", tag="button"` | Keyword args |
