# PyWebFlx

**Automação de navegador para páginas Chrome já abertas.**

PyWebFlx conecta a páginas já abertas no Chrome via uma extensão (Manifest V3) + WebSocket. Diferente do Selenium, não cria sandbox — você automatiza o navegador real.

## Instalacao

```bash
pip install pywebflx
pywebflx install-extension
```

## Quick Start

```python
import asyncio
from pywebflx import use_browser

async def main():
    async with use_browser(url="https://quotes.toscrape.com/") as browser:
        # Inspect — entender a pagina
        print(await browser.inspect(depth=5))

        # Extrair dados
        quotes = await browser.extract_data(
            container="body",
            row=".quote",
            columns={"texto": ".text", "autor": ".author"}
        )
        for q in quotes:
            print(f"{q['autor']}: {q['texto'][:60]}...")

asyncio.run(main())
```

## Principais funcionalidades

| Metodo | Descricao |
|--------|-----------|
| `use_browser()` | Conecta a aba por URL/titulo, abre se nao existir |
| `click()` | Clica (CSS, XPath ou texto) |
| `type_into()` | Digita em campos |
| `get_text()` | Extrai texto de elemento |
| `extract_data()` | Extrai dados estruturados (cards, listas) |
| `extract_table()` | Extrai tabelas HTML com paginacao |
| `inspect()` | Visao resumida do DOM (otimizado pra IA) |
| `wait_element()` | Espera elemento aparecer |
| `execute_js()` | Executa JavaScript na pagina |

## Documentacao

[https://theflexa.github.io/pywebflx/](https://theflexa.github.io/pywebflx/)

## Licenca

MIT
