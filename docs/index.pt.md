# PyWebFlx

**Automação de navegador para páginas Chrome já abertas.**

O PyWebFlx é uma biblioteca Python que se conecta a páginas já abertas no Chrome por meio de uma extensão (Manifest V3) + WebSocket. Diferente do Selenium, ele não cria uma instância sandbox -- você automatiza o navegador real do usuário.

---

## Início Rápido

```python
import asyncio
from pywebflx import use_browser

async def main():
    async with use_browser(url="https://quotes.toscrape.com/") as browser:
        # Ver estrutura da página
        structure = await browser.inspect(depth=5)
        print(structure)

        # Extrair dados
        quotes = await browser.extract_data(
            container="body",
            row=".quote",
            columns={"text": ".text", "author": ".author"}
        )
        for q in quotes:
            print(f"{q['author']}: {q['text'][:60]}...")

asyncio.run(main())
```

## Por que PyWebFlx?

| | PyWebFlx | Selenium | Playwright |
|---|---|---|---|
| Usa Chrome já aberto | :white_check_mark: | :x: | :x: |
| Reutiliza sessão/login | :white_check_mark: | :x: | :x: |
| API async/await | :white_check_mark: | :x: | :white_check_mark: |
| Sem WebDriver/binário | :white_check_mark: | :x: | :x: |
| Inspect otimizado para IA | :white_check_mark: | :x: | :x: |
| Setup | Extensão Chrome | WebDriver + config | `playwright install` |

## Como funciona

```
Script Python                   Extensão Chrome
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

- **`use_browser()`** -- Conecta a abas por URL ou título, abre se não encontrar
- **`click()`, `type_into()`** -- Interação com elementos (CSS, XPath, texto)
- **`get_text()`, `extract_data()`** -- Extração de dados estruturados
- **`inspect()`** -- Visão resumida do DOM, otimizada para IAs
- **`extract_table()`** -- Extração de tabelas HTML com paginação
- **`wait_element()`, `element_exists()`** -- Sincronização
- **`execute_js()`** -- JavaScript customizado
