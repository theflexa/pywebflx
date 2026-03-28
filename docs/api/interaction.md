# Interacao

Metodos para interagir com elementos na pagina: clicar, digitar, selecionar, etc.

---

## click

Clica em um elemento.

```python
await browser.click(selector, **kwargs)
```

### Parametros

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| `selector` | `str` | — | Seletor CSS ou XPath |
| `text` | `str` | `None` | Buscar por texto visivel |
| `tag` | `str` | `None` | Filtrar por tag HTML |
| `role` | `str` | `None` | Buscar por ARIA role |
| `name` | `str` | `None` | Buscar por ARIA label/name |
| `click_type` | `str` | `"single"` | `"single"` ou `"double"` |
| `mouse_button` | `str` | `"left"` | `"left"`, `"right"`, `"middle"` |
| `timeout` | `float` | config | Timeout em segundos |
| `retry` | `int` | config | Tentativas em caso de falha |
| `verify` | `str` | `None` | Seletor para verificar apos click |
| `delay_before` | `float` | `None` | Delay antes do click |
| `delay_after` | `float` | config | Delay apos o click |

### Exemplos

```python
# CSS selector
await browser.click("#btn-login")

# XPath
await browser.click("//button[@id='submit']")

# Por texto
await browser.click(text="Entrar", tag="button")

# Double click
await browser.click("#item", click_type="double")

# Click direito
await browser.click("#menu", mouse_button="right")

# Com retry e verificacao
await browser.click("#btn", retry=3, verify=".sucesso", timeout=10)
```

---

## type_into

Digita texto em um campo, simulando digitacao.

```python
await browser.type_into(selector, text="valor")
```

### Parametros

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| `selector` | `str` | — | Seletor do campo |
| `text` | `str` | `""` | Texto a digitar |
| `clear_before` | `bool` | `True` | Limpar campo antes |
| `click_before` | `bool` | `True` | Focar/clicar no campo antes |
| `delay_between_keys` | `float` | `0` | Delay entre teclas (0 = instantaneo) |
| `timeout` | `float` | config | Timeout |
| `retry` | `int` | config | Tentativas |

### Exemplos

```python
await browser.type_into("#email", text="usuario@email.com")
await browser.type_into("#senha", text="123456", delay_between_keys=0.05)
await browser.type_into("#campo", text="adicionar", clear_before=False)
```

---

## set_text

Define o valor de um campo diretamente, sem simular digitacao.

```python
await browser.set_text(selector, text="valor")
```

### Exemplo

```python
await browser.set_text("#campo-oculto", text="valor-direto")
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
await browser.check("#aceito-termos")
await browser.uncheck("#newsletter")
```

---

## select_item

Seleciona um item em um dropdown `<select>`.

```python
await browser.select_item(selector, item="valor", by="text")
```

### Parametros

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| `selector` | `str` | — | Seletor do `<select>` |
| `item` | `str` | `""` | Valor, texto ou indice a selecionar |
| `by` | `str` | `"text"` | `"text"`, `"value"` ou `"index"` |

### Exemplo

```python
await browser.select_item("#estado", "Para", by="text")
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
await browser.hover("#menu-dropdown")
```

---

## send_hotkey

Envia atalho de teclado.

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

Todos os metodos aceitam 3 tipos de seletor:

| Tipo | Exemplo | Deteccao |
|------|---------|----------|
| CSS | `"#btn"`, `".class"`, `"div > span"` | Padrao |
| XPath | `"//button[@id='ok']"`, `.//div` | Comeca com `//`, `./` ou `(` |
| Atributos | `text="Entrar", tag="button"` | Keyword args |
