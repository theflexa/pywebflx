import asyncio
from pywebflx import use_browser, configure_logging

configure_logging(level="INFO")

async def main():
    print("Aguardando extensao conectar...")
    async with use_browser(url="www.google.com") as browser:
        print("Conectado!")

        # Ver estrutura da pagina
        estrutura = await browser.inspect()
        print("\n--- Estrutura da pagina ---")
        print(estrutura)

        # Digitar no campo de busca
        await browser.type_into("[name='q']", text="PyWebFlx funciona!")
        print("\nDigitou no campo de busca!")

        # Pegar titulo da pagina
        titulo = await browser.execute_js("return document.title")
        print(f"Titulo da pagina: {titulo}")

asyncio.run(main())
