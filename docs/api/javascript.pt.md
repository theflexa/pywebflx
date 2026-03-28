# JavaScript

Métodos para executar JavaScript customizado na página.

---

## execute_js

Executa código JavaScript e retorna o resultado.

```python
result = await browser.execute_js("return document.title")
```

### Exemplos

```python
# Título da página
title = await browser.execute_js("return document.title")

# URL atual
url = await browser.execute_js("return window.location.href")

# Rolar até o final
await browser.execute_js("return window.scrollTo(0, document.body.scrollHeight)")
```

!!! note "Limitação"
    `execute_js` suporta expressões simples com `return`. Para lógica complexa, use `extract_data` ou manipule via `click`/`type_into`.

---

## inject_js

Executa JavaScript sem aguardar um valor de retorno.

```python
await browser.inject_js("window.scrollTo(0, 0)")
```

---

## switch_to (iframes)

Muda o contexto para dentro de um iframe.

```python
async with browser.switch_to("#iframe-content") as frame:
    await frame.click("#btn-inside-iframe")
    text = await frame.get_text(".result")
```

!!! warning "Em desenvolvimento"
    O suporte a iframes está planejado para a v2. Atualmente `switch_to` retorna o mesmo contexto.
