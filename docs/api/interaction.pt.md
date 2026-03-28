# Interação

Métodos para interagir com elementos na página: clicar, digitar, selecionar, etc.

---

## click

Clica em um elemento.

```python
await browser.click(selector, **kwargs)
```

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `selector` | `str` | -- | Seletor CSS ou XPath |
| `text` | `str` | `None` | Buscar por texto visível |
| `tag` | `str` | `None` | Filtrar por tag HTML |
| `role` | `str` | `None` | Buscar por role ARIA |
| `name` | `str` | `None` | Buscar por label/name ARIA |
| `click_type` | `str` | `"single"` | `"single"` ou `"double"` |
| `mouse_button` | `str` | `"left"` | `"left"`, `"right"`, `"middle"` |
| `timeout` | `float` | config | Timeout em segundos |
| `retry` | `int` | config | Tentativas de retentativa em caso de falha |
| `verify` | `str` | `None` | Seletor para verificar após o clique |
| `delay_before` | `float` | `None` | Atraso antes do clique |
| `delay_after` | `float` | config | Atraso após o clique |

### Exemplos

```python
# Seletor CSS
await browser.click("#btn-login")

# XPath
await browser.click("//button[@id='submit']")

# Por texto
await browser.click(text="Entrar", tag="button")

# Duplo clique
await browser.click("#item", click_type="double")

# Clique com botão direito
await browser.click("#menu", mouse_button="right")

# Com retentativa e verificação
await browser.click("#btn", retry=3, verify=".success", timeout=10)
```

---

## type_into

Digita texto em um campo, simulando teclas.

```python
await browser.type_into(selector, text="valor")
```

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `selector` | `str` | -- | Seletor do campo |
| `text` | `str` | `""` | Texto a digitar |
| `clear_before` | `bool` | `True` | Limpar campo antes de digitar |
| `click_before` | `bool` | `True` | Focar/clicar no campo antes de digitar |
| `delay_between_keys` | `float` | `0` | Atraso entre teclas (0 = instantâneo) |
| `timeout` | `float` | config | Timeout |
| `retry` | `int` | config | Tentativas de retentativa |

### Exemplos

```python
await browser.type_into("#email", text="usuario@email.com")
await browser.type_into("#password", text="123456", delay_between_keys=0.05)
await browser.type_into("#field", text="acrescentar", clear_before=False)
```

---

## set_text

Define o valor de um campo diretamente, sem simular teclas.

```python
await browser.set_text(selector, text="valor")
```

### Exemplo

```python
await browser.set_text("#hidden-field", text="valor-direto")
```

---

## check / uncheck

Marca ou desmarca um checkbox.

```python
await browser.check(selector)
await browser.uncheck(selector)
```

### Exemplo

```python
await browser.check("#aceitar-termos")
await browser.uncheck("#newsletter")
```

---

## select_item

Seleciona um item em um dropdown `<select>`.

```python
await browser.select_item(selector, item="valor", by="text")
```

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `selector` | `str` | -- | Seletor do `<select>` |
| `item` | `str` | `""` | Valor, texto ou índice a selecionar |
| `by` | `str` | `"text"` | `"text"`, `"value"` ou `"index"` |

### Exemplo

```python
await browser.select_item("#estado", "São Paulo", by="text")
await browser.select_item("#pais", "BR", by="value")
await browser.select_item("#mes", "0", by="index")
```

---

## hover

Passa o mouse sobre um elemento.

```python
await browser.hover(selector)
```

### Exemplo

```python
await browser.hover("#dropdown-menu")
```

---

## send_hotkey

Envia um atalho de teclado.

```python
await browser.send_hotkey(keys)
```

### Exemplos

```python
await browser.send_hotkey("ctrl+a")
await browser.send_hotkey("Enter")
await browser.send_hotkey("ctrl+shift+s")
```

---

## Seletores

Todos os métodos aceitam 3 tipos de seletores:

| Tipo | Exemplo | Detecção |
|------|---------|----------|
| CSS | `"#btn"`, `".class"`, `"div > span"` | Padrão |
| XPath | `"//button[@id='ok']"`, `.//div` | Começa com `//`, `./` ou `(` |
| Atributos | `text="Entrar", tag="button"` | Argumentos nomeados |
