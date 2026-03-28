# use_browser

Ponto de entrada principal do PyWebFlx. Conecta a uma aba Chrome e retorna um `BrowserContext` com todos os metodos de automacao.

## Assinatura

```python
async with use_browser(
    url: str = None,
    title: str = None,
    open: str = "if_not_open",
    config: PyWebFlxConfig = None,
) as browser:
    ...
```

## Parametros

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| `url` | `str` | `None` | URL para buscar (match parcial) e/ou abrir |
| `title` | `str` | `None` | Titulo da aba para buscar (match parcial) |
| `open` | `str` | `"if_not_open"` | Comportamento de abertura (ver abaixo) |
| `config` | `PyWebFlxConfig` | `None` | Configuracao customizada |

### Parametro `open`

Inspirado no UiPath:

| Valor | Comportamento |
|-------|--------------|
| `"if_not_open"` | Busca aba existente. Se nao encontrar, abre a `url`. **(padrao)** |
| `"open"` | Sempre abre nova aba com a `url`. |
| `"never"` | Apenas conecta a aba existente. Nunca abre. |

## Exemplos

### Basico — abre se nao existir

```python
async with use_browser(url="https://quotes.toscrape.com/") as browser:
    await browser.click("#btn")
```

### Buscar por titulo

```python
async with use_browser(title="Portal Sicoob", open="never") as browser:
    saldo = await browser.get_text(".saldo")
```

### Sempre abrir nova aba

```python
async with use_browser(url="https://example.com", open="open") as browser:
    await browser.type_into("#email", text="user@email.com")
```

### Com configuracao customizada

```python
from pywebflx import PyWebFlxConfig

config = PyWebFlxConfig(default_timeout=30, retry_count=3)

async with use_browser(url="https://example.com", config=config) as browser:
    await browser.click("#btn", timeout=60)  # 60 sobrescreve 30
```

### Multiplas abas

```python
async with use_browser(url="https://portal.com") as aba1:
    async with use_browser(url="https://email.com") as aba2:
        dado = await aba1.get_text(".saldo")
        await aba2.type_into("#corpo", text=dado)
```

## Excecoes

| Excecao | Quando |
|---------|--------|
| `BrowserNotFoundError` | Aba nao encontrada e `open="never"` |
| `ExtensionNotConnectedError` | Extensao Chrome nao esta conectada |
