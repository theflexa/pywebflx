# inspect

Returns a summarized view of the DOM structure, optimized for AI consumption and quick debugging.

Uses **~95% fewer tokens** than raw HTML while preserving useful information.

## Signature

```python
structure = await browser.inspect(selector="", depth=2, samples=2)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `selector` | `str` | `""` | Scope (empty = entire page) |
| `depth` | `int` | `2` | Maximum traversal depth |
| `samples` | `int` | `2` | Data samples in lists/tables |

## Output example

```
<body>
  <header#top-nav .navbar>
    <button.btn-menu> "Menu"
    <input#search type="search" placeholder="Search...">
    <a.logo> "Portal Sicoob"
  <main#content>
    <form#login-form>
      <input#username type="text" placeholder="Username" [required]>
      <input#password type="password" placeholder="Password" [required]>
      <select#branch> 3 options: ["0001 - Downtown", "0032 - Belem"]
      <button#btn-login type="submit"> "Sign In"
    <div.notices>
      <table#notices-table> 3 cols x 12 rows
        headers: ["Date", "Type", "Message"]
        sample[0]: ["03/28", "Info", "Scheduled maintenance"]
```

## Usage workflow

### 1. General inspect -- understand the page

```python
structure = await browser.inspect(depth=5, samples=2)
print(structure)
```

Result:
```
<div.quote> x 10 items
  sample[0]: "The world as we have created it..."
```

### 2. Focused inspect -- view inside an element

```python
detail = await browser.inspect(".quote", depth=5)
print(detail)
```

Result:
```
<div.quote>
  <span.text> "The world as we have created it..."
  <span>
    <small.author> "Albert Einstein"
  <div.tags>
    <a.tag> x 3 items
      sample[0]: "change"
```

### 3. Use the discovered selectors

```python
quotes = await browser.extract_data(
    container="body",
    row=".quote",
    columns={"text": ".text", "author": ".author"}
)
```

## What inspect shows

| Element | How it appears |
|---------|---------------|
| IDs and classes | `<div#login-form.container>` |
| Inputs | `<input#email type="text" placeholder="Email" [required]>` |
| Links | `<a.logo href="/home">` |
| Text | `<button> "Sign In"` |
| Tables | `<table> 3 cols x 12 rows` + headers + samples |
| Selects | `<select> 5 options: ["Opt1", "Opt2", ...]` |
| Lists | `<div.card> x 20 items` + samples |

## When to use

| Scenario | Command |
|----------|---------|
| Understand an unknown page | `inspect(depth=5)` |
| Find selectors for automation | `inspect(".container", depth=5)` |
| Feed AI with page context | `inspect(depth=3, samples=2)` |
| Quick debug without DevTools | `inspect()` |
