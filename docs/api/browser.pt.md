# use_browser

Ponto de entrada principal do PyWebFlx. Conecta a uma aba do Chrome e retorna um `BrowserContext` com todos os métodos de automação.

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

## Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `url` | `str` | `None` | URL para buscar (correspondência parcial) e/ou abrir |
| `title` | `str` | `None` | Título da aba para buscar (correspondência parcial) |
| `open` | `str` | `"if_not_open"` | Comportamento de abertura (veja abaixo) |
| `config` | `PyWebFlxConfig` | `None` | Configuração personalizada |

### Parâmetro `open`

| Valor | Comportamento |
|-------|---------------|
| `"if_not_open"` | Busca uma aba existente. Se não encontrar, abre a `url`. **(padrão)** |
| `"open"` | Sempre abre uma nova aba com a `url`. |
| `"never"` | Apenas conecta a uma aba existente. Nunca abre. |

## Exemplos

### Básico -- abre se não encontrar

```python
async with use_browser(url="https://quotes.toscrape.com/") as browser:
    await browser.click("#btn")
```

### Buscar por título

```python
async with use_browser(title="Portal Sicoob", open="never") as browser:
    balance = await browser.get_text(".balance")
```

### Sempre abrir uma nova aba

```python
async with use_browser(url="https://example.com", open="open") as browser:
    await browser.type_into("#email", text="user@email.com")
```

### Com configuração personalizada

```python
from pywebflx import PyWebFlxConfig

config = PyWebFlxConfig(default_timeout=30, retry_count=3)

async with use_browser(url="https://example.com", config=config) as browser:
    await browser.click("#btn", timeout=60)  # 60 sobrescreve 30
```

### Múltiplas abas

```python
async with use_browser(url="https://portal.com") as tab1:
    async with use_browser(url="https://email.com") as tab2:
        data = await tab1.get_text(".balance")
        await tab2.type_into("#body", text=data)
```

## Exceções

| Exceção | Quando |
|---------|--------|
| `BrowserNotFoundError` | Aba não encontrada e `open="never"` |
| `ExtensionNotConnectedError` | Extensão do Chrome não está conectada |
