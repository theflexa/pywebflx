# Exemplo: Automacao RPA

Exemplo de automacao de portal web usando PyWebFlx, inspirado em fluxos UiPath.

## Cenario

Automatizar login em um portal, extrair dados de uma tabela e salvar.

## Codigo completo

```python
import asyncio
import pandas as pd
from pywebflx import use_browser, PyWebFlxConfig, configure_logging

configure_logging(level="INFO")

config = PyWebFlxConfig(
    default_timeout=15,
    retry_count=2,
    delay_between_actions=0.5,
)

async def main():
    # 1. Conectar ao portal (abre se nao estiver aberto)
    async with use_browser(
        url="https://portal.example.com",
        config=config,
    ) as browser:

        # 2. Login
        await browser.type_into("#usuario", text="joao@empresa.com")
        await browser.type_into("#senha", text="minha-senha")
        await browser.click("#btn-login")

        # 3. Esperar dashboard carregar
        await browser.wait_element(".dashboard", timeout=10)
        await browser.wait_element_vanish("#spinner")

        # 4. Navegar para relatorio
        await browser.click(text="Relatorios", tag="a")
        await browser.wait_element("#tabela-clientes")

        # 5. Extrair tabela
        dados = await browser.extract_table(
            "#tabela-clientes",
            next_page="#btn-proxima",
            max_pages=5,
        )

        # 6. Salvar em Excel
        df = pd.DataFrame(dados)
        df.to_excel("clientes.xlsx", index=False)
        print(f"Exportados {len(dados)} registros")

asyncio.run(main())
```

## Fluxo com multiplas abas

```python
async def transferir_dados():
    async with use_browser(url="https://portal.com") as portal:
        async with use_browser(url="https://email.com") as email:
            # Extrair dado do portal
            saldo = await portal.get_text(".saldo-conta")

            # Colar no email
            await email.click("#novo-email")
            await email.type_into("#assunto", text="Saldo diario")
            await email.type_into("#corpo", text=f"Saldo: {saldo}")
            await email.click("#btn-enviar")
```

## Fluxo com tratamento de erros

```python
from pywebflx import (
    use_browser,
    ElementNotFoundError,
    BrowserNotFoundError,
    ElementTimeoutError,
)

async def automacao_robusta():
    try:
        async with use_browser(url="https://portal.com") as browser:

            # Tentar clicar com retry
            await browser.click(
                "#btn-critico",
                retry=3,
                verify=".resultado-sucesso",
                timeout=10,
            )

    except BrowserNotFoundError:
        print("Portal nao esta aberto")

    except ElementTimeoutError as e:
        print(f"Elemento {e.selector} nao apareceu em {e.timeout}s")

    except ElementNotFoundError as e:
        print(f"Elemento {e.selector} nao encontrado")
```

## Fluxo com dropdown e checkbox

```python
async def preencher_formulario():
    async with use_browser(url="https://portal.com/cadastro") as browser:
        await browser.type_into("#nome", text="Joao Silva")
        await browser.type_into("#cpf", text="123.456.789-00")
        await browser.select_item("#estado", "Para", by="text")
        await browser.check("#aceito-termos")
        await browser.click("#btn-cadastrar")
        await browser.wait_element(".msg-sucesso", timeout=10)
```
