# JavaScript

Metodos para executar JavaScript customizado na pagina.

---

## execute_js

Executa codigo JavaScript e retorna o resultado.

```python
resultado = await browser.execute_js("return document.title")
```

### Exemplos

```python
# Titulo da pagina
titulo = await browser.execute_js("return document.title")

# URL atual
url = await browser.execute_js("return window.location.href")

# Scroll ate o final
await browser.execute_js("return window.scrollTo(0, document.body.scrollHeight)")
```

!!! note "Limitacao"
    O `execute_js` suporta expressoes simples com `return`. Para logica complexa, use `extract_data` ou manipule via `click`/`type_into`.

---

## inject_js

Executa JavaScript sem esperar retorno.

```python
await browser.inject_js("window.scrollTo(0, 0)")
```

---

## switch_to (iframes)

Muda o contexto para dentro de um iframe.

```python
async with browser.switch_to("#iframe-conteudo") as frame:
    await frame.click("#btn-dentro-do-iframe")
    texto = await frame.get_text(".resultado")
```

!!! warning "Em desenvolvimento"
    O suporte a iframes esta planejado para v2. Atualmente o `switch_to` retorna o mesmo contexto.
