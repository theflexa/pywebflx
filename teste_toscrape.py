import asyncio
from pywebflx import use_browser, configure_logging

configure_logging(level="INFO")

async def main():
    print("Aguardando extensao conectar...")
    async with use_browser(
        url="toscrape.com",
        if_not_open="https://toscrape.com"
    ) as browser:
        print("Conectado!\n")

        # Inspect com mais profundidade pra ver os links
        estrutura = await browser.inspect(depth=5, samples=3)
        print("--- Estrutura da pagina ---")
        print(estrutura.encode("ascii", errors="replace").decode())

        # Clicar no link "Default" (3 formas)
        print("\nClicando em 'Default'...")

        # Forma 1: por texto
        await browser.click(text="Default", tag="a")

        # Forma 2 seria: por CSS
        # await browser.click("a[href='http://quotes.toscrape.com/']")

        # Forma 3 seria: por XPath
        # await browser.click("//a[text()='Default']")

        print("Clicou! Verificando nova pagina...")
        titulo = await browser.execute_js("return document.title")
        print(f"Titulo: {titulo}")

asyncio.run(main())
