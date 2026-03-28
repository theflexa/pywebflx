# Exemplo: Automação RPA

Exemplo de automação de portal web usando PyWebFlx.

## Cenário

Automatizar login em um portal, extrair dados de uma tabela e salvar.

## Código completo

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
    # 1. Conectar ao portal (abre se não estiver aberto)
    async with use_browser(
        url="https://portal.example.com",
        config=config,
    ) as browser:

        # 2. Login
        await browser.type_into("#username", text="joao@empresa.com")
        await browser.type_into("#password", text="minha-senha")
        await browser.click("#btn-login")

        # 3. Aguardar o painel carregar
        await browser.wait_element(".dashboard", timeout=10)
        await browser.wait_element_vanish("#spinner")

        # 4. Navegar para relatórios
        await browser.click(text="Relatórios", tag="a")
        await browser.wait_element("#clients-table")

        # 5. Extrair tabela
        data = await browser.extract_table(
            "#clients-table",
            next_page="#btn-next",
            max_pages=5,
        )

        # 6. Salvar em Excel
        df = pd.DataFrame(data)
        df.to_excel("clientes.xlsx", index=False)
        print(f"Exportados {len(data)} registros")

asyncio.run(main())
```

## Fluxo com múltiplas abas

```python
async def transferir_dados():
    async with use_browser(url="https://portal.com") as portal:
        async with use_browser(url="https://email.com") as email:
            # Extrair dados do portal
            saldo = await portal.get_text(".account-balance")

            # Colar no email
            await email.click("#new-email")
            await email.type_into("#subject", text="Saldo diário")
            await email.type_into("#body", text=f"Saldo: {saldo}")
            await email.click("#btn-send")
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

            # Tentar clicar com retentativa
            await browser.click(
                "#critical-btn",
                retry=3,
                verify=".success-result",
                timeout=10,
            )

    except BrowserNotFoundError:
        print("Portal não está aberto")

    except ElementTimeoutError as e:
        print(f"Elemento {e.selector} não apareceu em {e.timeout}s")

    except ElementNotFoundError as e:
        print(f"Elemento {e.selector} não encontrado")
```

## Fluxo com dropdown e checkbox

```python
async def preencher_formulario():
    async with use_browser(url="https://portal.com/cadastro") as browser:
        await browser.type_into("#nome", text="João Silva")
        await browser.type_into("#cpf", text="123.456.789-00")
        await browser.select_item("#estado", "São Paulo", by="text")
        await browser.check("#aceitar-termos")
        await browser.click("#btn-cadastrar")
        await browser.wait_element(".success-msg", timeout=10)
```
