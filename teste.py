import asyncio
from pywebflx import use_browser, configure_logging

configure_logging(level="INFO")

async def main():
    print("Aguardando extensao conectar...")
    async with use_browser(url="https://toscrape.com/") as browser:
        print("Conectado!")

        # Ver estrutura da pagina
        estrutura = await browser.inspect()
        print("\n--- Estrutura da pagina ---")
        print(estrutura)

        # Digitar no campo de busca
        await browser.click("//*/tbody/tr[2]/td[1]/a")
        print("\nClicou no botao de login!")      

        # Pegar titulo da pagina
        titulo = await browser.execute_js("return document.title")
        print(f"Titulo da pagina: {titulo}")

asyncio.run(main())
