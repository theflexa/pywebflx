# Exemplo: Web Scraping

Scraping completo do site [quotes.toscrape.com](https://quotes.toscrape.com/) usando PyWebFlx.

## O fluxo

1. **`inspect()`** -- entender a pagina
2. **`inspect(".quote")`** -- ver a estrutura interna
3. **`extract_data()`** -- extrair usando os seletores descobertos

## Codigo completo

```python
import asyncio
from pywebflx import use_browser, configure_logging

configure_logging(level="INFO")

async def main():
    async with use_browser(url="https://quotes.toscrape.com/") as browser:

        # 1. Inspect geral -- descobre .quote x 10
        page = await browser.inspect(depth=5, samples=1)
        print(page)
        # <div.quote> x 10 items
        #   sample[0]: "A reader lives a thousand lives..."

        # 2. Inspect focado -- descobre .text, .author, .tags
        quote = await browser.inspect(".quote", depth=5, samples=1)
        print(quote)
        # <span.text> "A reader lives..."
        # <small.author> "George R.R. Martin"
        # <a.tag> x 4 items

        # 3. Extrair usando os seletores descobertos
        quotes = await browser.extract_data(
            container="body",
            row=".quote",
            columns={
                "text": ".text",
                "author": ".author",
                "tags": ".tags",
            }
        )

        for i, q in enumerate(quotes, 1):
            tags = [t.strip() for t in q['tags'].replace("Tags:", "").split("\n") if t.strip()]
            print(f"{i}. {q['author']}: {q['text'][:60]}...")
            print(f"   Tags: {', '.join(tags)}")

        print(f"\nTotal: {len(quotes)} citacoes")

asyncio.run(main())
```

## Saida

```
1. George R.R. Martin: "A reader lives a thousand lives before he dies...
   Tags: read, readers, reading, reading-books
2. C.S. Lewis: "You can never get a cup of tea large enough or a book...
   Tags: books, tea
3. Marilyn Monroe: "You believe lies so you eventually learn to trust...
   Tags: lies, lying, trust
...
Total: 10 citacoes
```

## Com paginacao

```python
async def scrape_todas_paginas():
    async with use_browser(url="https://quotes.toscrape.com/") as browser:
        todas_citacoes = []
        pagina = 1

        while True:
            print(f"Pagina {pagina}...")

            quotes = await browser.extract_data(
                container="body",
                row=".quote",
                columns={"text": ".text", "author": ".author"}
            )
            todas_citacoes.extend(quotes)

            # Verificar se ha proxima pagina
            if not await browser.element_exists("li.next a"):
                break

            await browser.click("li.next a")
            await asyncio.sleep(1)
            pagina += 1

        print(f"Total: {len(todas_citacoes)} citacoes em {pagina} paginas")
        return todas_citacoes
```

## Exportar para CSV

```python
import pandas as pd

quotes = await scrape_todas_paginas()
df = pd.DataFrame(quotes)
df.to_csv("citacoes.csv", index=False)
```

## Exportar para JSON

```python
import json

with open("citacoes.json", "w") as f:
    json.dump(quotes, f, indent=2, ensure_ascii=False)
```
