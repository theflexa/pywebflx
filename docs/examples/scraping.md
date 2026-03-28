# Exemplo: Web Scraping

Scraping completo do site [quotes.toscrape.com](https://quotes.toscrape.com/) usando PyWebFlx.

## O fluxo

1. **`inspect()`** — entender a pagina
2. **`inspect(".quote")`** — ver estrutura interna
3. **`extract_data()`** — extrair com os seletores descobertos

## Codigo completo

```python
import asyncio
from pywebflx import use_browser, configure_logging

configure_logging(level="INFO")

async def main():
    async with use_browser(url="https://quotes.toscrape.com/") as browser:

        # 1. Inspect geral — descobre que tem .quote x 10
        pagina = await browser.inspect(depth=5, samples=1)
        print(pagina)
        # <div.quote> x 10 items
        #   sample[0]: "A reader lives a thousand lives..."

        # 2. Inspect focado — descobre .text, .author, .tags
        quote = await browser.inspect(".quote", depth=5, samples=1)
        print(quote)
        # <span.text> "A reader lives..."
        # <small.author> "George R.R. Martin"
        # <a.tag> x 4 items

        # 3. Extract com os seletores descobertos
        quotes = await browser.extract_data(
            container="body",
            row=".quote",
            columns={
                "texto": ".text",
                "autor": ".author",
                "tags": ".tags",
            }
        )

        for i, q in enumerate(quotes, 1):
            tags = [t.strip() for t in q['tags'].replace("Tags:", "").split("\n") if t.strip()]
            print(f"{i}. {q['autor']}: {q['texto'][:60]}...")
            print(f"   Tags: {', '.join(tags)}")

        print(f"\nTotal: {len(quotes)} quotes")

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
Total: 10 quotes
```

## Com paginacao

```python
async def scrape_all_pages():
    async with use_browser(url="https://quotes.toscrape.com/") as browser:
        all_quotes = []
        page = 1

        while True:
            print(f"Pagina {page}...")

            quotes = await browser.extract_data(
                container="body",
                row=".quote",
                columns={"texto": ".text", "autor": ".author"}
            )
            all_quotes.extend(quotes)

            # Verificar se tem proxima pagina
            if not await browser.element_exists("li.next a"):
                break

            await browser.click("li.next a")
            await asyncio.sleep(1)
            page += 1

        print(f"Total: {len(all_quotes)} quotes em {page} paginas")
        return all_quotes
```

## Exportar para CSV

```python
import pandas as pd

quotes = await scrape_all_pages()
df = pd.DataFrame(quotes)
df.to_csv("quotes.csv", index=False)
```

## Exportar para JSON

```python
import json

with open("quotes.json", "w") as f:
    json.dump(quotes, f, indent=2, ensure_ascii=False)
```
