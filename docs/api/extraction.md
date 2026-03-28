# Data Extraction

Methods for extracting text, attributes, and structured data from the page.

---

## get_text

Returns the visible text of an element.

```python
text = await browser.get_text(selector)
```

### Example

```python
balance = await browser.get_text(".account-balance")
# "$1,200.00"

title = await browser.get_text("h1")
# "Dashboard"
```

---

## get_attribute

Returns the value of an HTML attribute.

```python
value = await browser.get_attribute(selector, attribute="name")
```

### Example

```python
href = await browser.get_attribute("a.report", attribute="href")
# "https://portal.com/report.pdf"

css_class = await browser.get_attribute("#btn", attribute="class")
# "btn btn-primary"
```

---

## get_full_text

Returns all visible text on the page.

```python
text = await browser.get_full_text()
```

---

## extract_data

Extracts structured data from repetitive elements (cards, lists, divs).

```python
data = await browser.extract_data(
    container="parent-selector",
    row="each-item-selector",
    columns={"column_name": "inner-selector"},
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `container` | `str` | `""` | Parent container selector |
| `row` | `str` | `""` | Selector for each repeated item |
| `columns` | `dict` | `None` | Name -> inner selector mapping |
| `next_page` | `str` | `None` | "Next page" button selector |
| `max_pages` | `int` | `100` | Maximum pages to extract |

### Return

List of dicts:

```python
[
    {"text": "Quote 1...", "author": "Einstein"},
    {"text": "Quote 2...", "author": "Tolkien"},
]
```

### Example -- Quotes

```python
quotes = await browser.extract_data(
    container="body",
    row=".quote",
    columns={
        "text": ".text",
        "author": ".author",
        "tags": ".tags",
    }
)
```

### Example -- Product cards

```python
products = await browser.extract_data(
    container="#product-list",
    row=".product-card",
    columns={
        "Name": ".card-title",
        "Price": ".card-price",
        "Stock": ".card-stock span",
    },
    next_page="#btn-next",
    max_pages=5,
)
```

### How to discover selectors

Use `inspect()` to map the structure:

```python
# 1. View the general page
await browser.inspect(depth=5)
# Shows: <div.quote> x 10 items

# 2. View inside an item
await browser.inspect(".quote", depth=5)
# Shows: <span.text>, <small.author>, <a.tag>

# 3. Use in extract_data
data = await browser.extract_data(
    container="body", row=".quote",
    columns={"text": ".text", "author": ".author"}
)
```

---

## extract_table

Extracts data from an HTML `<table>`. Uses headers as keys.

```python
data = await browser.extract_table(selector)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `selector` | `str` | -- | `<table>` selector |
| `next_page` | `str` | `None` | Next page button selector |
| `max_pages` | `int` | `100` | Maximum pages |

### Return

```python
[
    {"Name": "John", "SSN": "123-45-6789", "Balance": "1,200.00"},
    {"Name": "Mary", "SSN": "987-65-4321", "Balance": "3,500.00"},
]
```

### Example

```python
# Simple table
clients = await browser.extract_table("#clients-table")

# With pagination
clients = await browser.extract_table(
    "#clients-table",
    next_page="#btn-next",
    max_pages=10,
)

# Convert to DataFrame
import pandas as pd
df = pd.DataFrame(clients)
```
