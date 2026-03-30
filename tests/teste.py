import asyncio
from pywebflx import use_browser, configure_logging

configure_logging(level="INFO")

async def main():
    async with use_browser(url="https://quotes.toscrape.com/") as browser:

        # 1. Inspect geral — descobre que tem .quote x 10
        print("=== Inspect geral ===")
        pagina = await browser.inspect(depth=5, samples=1)

        # 2. Inspect focado — descobre .text, .author, .tags
        print("\n=== Inspect de um .quote ===")
        quote = await browser.inspect(".quote", depth=5, samples=1)

        # 3. Extract com os seletores descobertos
        print("\n=== Extraindo quotes ===")
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
            texto = q['texto'].strip('\u201c\u201d"')[:80]
            tags = [t.strip() for t in q['tags'].replace("Tags:", "").split("\n") if t.strip()]
            print(f"\n{i}. \"{texto}...\"")
            print(f"   -- {q['autor']}")
            print(f"   Tags: {', '.join(tags)}")

        print(f"\nTotal: {len(quotes)} quotes")

asyncio.run(main())
