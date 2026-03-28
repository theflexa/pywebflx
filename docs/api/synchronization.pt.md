# Sincronização

Métodos para aguardar elementos aparecerem, desaparecerem ou verificar existência.

---

## element_exists

Verifica se um elemento existe na página.

```python
exists = await browser.element_exists(selector, timeout=0)
```

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `selector` | `str` | -- | Seletor CSS ou XPath |
| `timeout` | `float` | `0` | Se > 0, aguarda até N segundos |

### Exemplos

```python
# Verificação instantânea
if await browser.element_exists("#success-modal"):
    print("Sucesso!")

# Aguardar até 5 segundos
if await browser.element_exists("#result", timeout=5):
    text = await browser.get_text("#result")
```

---

## wait_element

Aguarda um elemento atender a uma condição. Lança erro em caso de timeout.

```python
await browser.wait_element(selector, condition="visible", timeout=None)
```

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `selector` | `str` | -- | Seletor CSS ou XPath |
| `condition` | `str` | `"visible"` | `"visible"`, `"clickable"`, `"present"` |
| `timeout` | `float` | config | Timeout em segundos |

### Exemplo

```python
await browser.wait_element("#loading", condition="visible", timeout=10)
await browser.click("#loading")
```

### Exceção

Lança `ElementTimeoutError` se a condição não for atendida dentro do timeout.

---

## wait_element_vanish

Aguarda um elemento desaparecer da página.

```python
await browser.wait_element_vanish(selector, timeout=None)
```

### Exemplo

```python
await browser.click("#btn-save")
await browser.wait_element_vanish("#spinner", timeout=15)
print("Salvo com sucesso!")
```

### Exceção

Lança `ElementTimeoutError` se o elemento ainda existir após o timeout.

---

## find_element

Encontra um elemento e retorna informações sobre ele.

```python
info = await browser.find_element(selector)
```

### Retorno

```python
{
    "tag": "button",
    "id": "btn-login",
    "classes": ["btn", "btn-primary"],
    "text": "Entrar",
    "visible": True,
}
```

### Exemplo

```python
el = await browser.find_element("#btn-submit")
if el["visible"]:
    await browser.click("#btn-submit")
```
