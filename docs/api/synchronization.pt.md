# Sincronizacao

Metodos para aguardar elementos aparecerem, desaparecerem ou verificar existencia.

---

## element_exists

Verifica se um elemento existe na pagina.

```python
exists = await browser.element_exists(selector, timeout=0)
```

### Parametros

| Parametro | Tipo | Padrao | Descricao |
|-----------|------|--------|-----------|
| `selector` | `str` | -- | Seletor CSS ou XPath |
| `timeout` | `float` | `0` | Se > 0, aguarda ate N segundos |

### Exemplos

```python
# Verificacao instantanea
if await browser.element_exists("#success-modal"):
    print("Sucesso!")

# Aguardar ate 5 segundos
if await browser.element_exists("#result", timeout=5):
    text = await browser.get_text("#result")
```

---

## wait_element

Aguarda um elemento atender a uma condicao. Lanca erro em caso de timeout.

```python
await browser.wait_element(selector, condition="visible", timeout=None)
```

### Parametros

| Parametro | Tipo | Padrao | Descricao |
|-----------|------|--------|-----------|
| `selector` | `str` | -- | Seletor CSS ou XPath |
| `condition` | `str` | `"visible"` | `"visible"`, `"clickable"`, `"present"` |
| `timeout` | `float` | config | Timeout em segundos |

### Exemplo

```python
await browser.wait_element("#loading", condition="visible", timeout=10)
await browser.click("#loading")
```

### Excecao

Lanca `ElementTimeoutError` se a condicao nao for atendida dentro do timeout.

---

## wait_element_vanish

Aguarda um elemento desaparecer da pagina.

```python
await browser.wait_element_vanish(selector, timeout=None)
```

### Exemplo

```python
await browser.click("#btn-save")
await browser.wait_element_vanish("#spinner", timeout=15)
print("Salvo com sucesso!")
```

### Excecao

Lanca `ElementTimeoutError` se o elemento ainda existir apos o timeout.

---

## find_element

Encontra um elemento e retorna informacoes sobre ele.

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
