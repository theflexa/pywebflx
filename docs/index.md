# PyWebFlx

**Browser automation para paginas Chrome ja abertas, inspirado na UiPath.**

PyWebFlx e uma biblioteca Python que se conecta a paginas ja abertas no Chrome via uma extensao (Manifest V3) + WebSocket. Diferente do Selenium, nao cria uma instancia sandbox — voce automatiza o navegador real do usuario.

---

## Quick Start

```python
import asyncio
from pywebflx import use_browser

async def main():
    async with use_browser(url="https://quotes.toscrape.com/") as browser:
        # Ver estrutura da pagina
        estrutura = await browser.inspect(depth=5)
        print(estrutura)

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

## Por que PyWebFlx?

| | PyWebFlx | Selenium | Playwright |
|---|---|---|---|
| Usa Chrome ja aberto | :white_check_mark: | :x: | :x: |
| Reaproveita sessao/login | :white_check_mark: | :x: | :x: |
| API async/await | :white_check_mark: | :x: | :white_check_mark: |
| Sem WebDriver/binario | :white_check_mark: | :x: | :x: |
| Inspect otimizado pra IA | :white_check_mark: | :x: | :x: |
| Setup | Extensao Chrome | WebDriver + config | `playwright install` |

## Como funciona

```
Script Python                    Chrome Extension
      |                                |
      |  1. Inicia WebSocket :9819     |
      |<------------------------------>|  2. Conecta automaticamente
      |                                |
      |  3. Comando JSON               |
      |------------------------------->|  4. Injeta script na aba
      |                                |     via chrome.scripting
      |  5. Resultado JSON             |
      |<-------------------------------|
      |                                |
```

## Principais funcionalidades

- **`use_browser()`** — Conecta a abas por URL ou titulo, abre se nao existir
- **`click()`, `type_into()`** — Interacao com elementos (CSS, XPath, texto)
- **`get_text()`, `extract_data()`** — Extracao de dados estruturados
- **`inspect()`** — Visao resumida do DOM, otimizada para IAs
- **`extract_table()`** — Extracao de tabelas HTML com paginacao
- **`wait_element()`, `element_exists()`** — Sincronizacao
- **`execute_js()`** — JavaScript customizado
