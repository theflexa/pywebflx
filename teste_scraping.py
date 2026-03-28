"""
Demo: Web scraping de https://quotes.toscrape.com/ com PyWebFlx

Fluxo:
1. inspect() para entender a estrutura da pagina
2. Com base no inspect, extrair dados com get_text, extract_table, extract_data
3. Navegar entre paginas
"""

import asyncio
import json
from pywebflx import use_browser, configure_logging

configure_logging(level="INFO")


async def main():
    print("Aguardando extensao conectar...")
    async with use_browser(url="https://quotes.toscrape.com/") as browser:
        print("Conectado!\n")

        # ---------------------------------------------------------------
        # PASSO 1: inspect() para entender a pagina
        # ---------------------------------------------------------------
        print("=" * 60)
        print("  PASSO 1: inspect() - Entender a estrutura da pagina")
        print("=" * 60)

        estrutura = await browser.inspect(depth=4, samples=2)
        print(estrutura.encode("ascii", errors="replace").decode())

        # ---------------------------------------------------------------
        # PASSO 2: get_text() - Extrair textos individuais
        # ---------------------------------------------------------------
        print("\n" + "=" * 60)
        print("  PASSO 2: get_text() - Extrair textos individuais")
        print("=" * 60)

        # O inspect mostrou que quotes estao em .quote > .text
        primeiro_quote = await browser.get_text(".quote .text")
        print(f"\nPrimeiro quote: {primeiro_quote}")

        primeiro_autor = await browser.get_text(".quote .author")
        print(f"Autor: {primeiro_autor}")

        # ---------------------------------------------------------------
        # PASSO 3: extract_data() - Extrair todos os quotes da pagina
        # ---------------------------------------------------------------
        print("\n" + "=" * 60)
        print("  PASSO 3: extract_data() - Extrair todos os quotes")
        print("=" * 60)

        quotes = await browser.extract_data(
            container="body",
            row=".quote",
            columns={
                "texto": ".text",
                "autor": ".author",
                "tags": ".tags",
            }
        )

        print(f"\nEncontrados {len(quotes)} quotes nesta pagina:\n")
        for i, q in enumerate(quotes, 1):
            texto = q['texto'][:80] + "..." if len(q['texto']) > 80 else q['texto']
            print(f"  {i}. {texto}")
            print(f"     -- {q['autor']}")
            print(f"     Tags: {q['tags'][:60]}")
            print()

        # ---------------------------------------------------------------
        # PASSO 4: Navegar para proxima pagina e extrair mais
        # ---------------------------------------------------------------
        print("=" * 60)
        print("  PASSO 4: Navegar para proxima pagina")
        print("=" * 60)

        # Verificar se existe botao "Next"
        tem_next = await browser.element_exists("li.next a")
        print(f"\nTem proxima pagina? {tem_next}")

        if tem_next:
            await browser.click("li.next a")
            await asyncio.sleep(1)  # Esperar carregar

            titulo = await browser.execute_js("return document.title")
            print(f"Titulo da nova pagina: {titulo}")

            # Extrair quotes da pagina 2
            quotes_p2 = await browser.extract_data(
                container="body",
                row=".quote",
                columns={
                    "texto": ".text",
                    "autor": ".author",
                }
            )
            print(f"Quotes na pagina 2: {len(quotes_p2)}")
            for q in quotes_p2[:3]:
                print(f"  - {q['autor']}: {q['texto'][:60]}...")

        # ---------------------------------------------------------------
        # PASSO 5: execute_js() - Titulo da pagina
        # ---------------------------------------------------------------
        print("\n" + "=" * 60)
        print("  PASSO 5: execute_js()")
        print("=" * 60)

        titulo = await browser.execute_js("return document.title")
        url = await browser.execute_js("return window.location.href")
        total_quotes = await browser.execute_js(
            "return document.querySelectorAll('.quote').length"
        )
        print(f"\nTitulo: {titulo}")
        print(f"URL: {url}")
        print(f"Quotes nesta pagina: {total_quotes}")

        print("\n" + "=" * 60)
        print("  DONE! Scraping completo.")
        print("=" * 60)


asyncio.run(main())
