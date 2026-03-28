# Extracao de Dados

Metodos para extrair textos, atributos e dados estruturados da pagina.

---

## get_text

Retorna o texto visivel de um elemento.

```python
texto = await browser.get_text(selector)
```

### Exemplo

```python
saldo = await browser.get_text(".saldo-conta")
# "R$ 1.200,00"

titulo = await browser.get_text("h1")
# "Portal Sicoob"
```

---

## get_attribute

Retorna o valor de um atributo HTML.

```python
valor = await browser.get_attribute(selector, attribute="nome")
```

### Exemplo

```python
href = await browser.get_attribute("a.relatorio", attribute="href")
# "https://portal.com/relatorio.pdf"

classe = await browser.get_attribute("#btn", attribute="class")
# "btn btn-primary"
```

---

## get_full_text

Retorna todo o texto visivel da pagina.

```python
texto = await browser.get_full_text()
```

---

## extract_data

Extrai dados estruturados de elementos repetitivos (cards, listas, divs).

```python
dados = await browser.extract_data(
    container="seletor-pai",
    row="seletor-de-cada-item",
    columns={"nome_coluna": "seletor-interno"},
)
```

### Parametros

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| `container` | `str` | `""` | Seletor do container pai |
| `row` | `str` | `""` | Seletor de cada item repetido |
| `columns` | `dict` | `None` | Mapeamento nome -> seletor interno |
| `next_page` | `str` | `None` | Seletor do botao "proxima pagina" |
| `max_pages` | `int` | `100` | Maximo de paginas a extrair |

### Retorno

Lista de dicts:

```python
[
    {"texto": "Quote 1...", "autor": "Einstein"},
    {"texto": "Quote 2...", "autor": "Tolkien"},
]
```

### Exemplo — Quotes

```python
quotes = await browser.extract_data(
    container="body",
    row=".quote",
    columns={
        "texto": ".text",
        "autor": ".author",
        "tags": ".tags",
    }
)
```

### Exemplo — Cards de produtos

```python
produtos = await browser.extract_data(
    container="#lista-produtos",
    row=".card-produto",
    columns={
        "Nome": ".card-title",
        "Preco": ".card-preco",
        "Estoque": ".card-estoque span",
    },
    next_page="#btn-proxima",
    max_pages=5,
)
```

### Como descobrir os seletores

Use `inspect()` para mapear a estrutura:

```python
# 1. Ver a pagina geral
await browser.inspect(depth=5)
# Mostra: <div.quote> x 10 items

# 2. Ver dentro de um item
await browser.inspect(".quote", depth=5)
# Mostra: <span.text>, <small.author>, <a.tag>

# 3. Usar no extract_data
dados = await browser.extract_data(
    container="body", row=".quote",
    columns={"texto": ".text", "autor": ".author"}
)
```

---

## extract_table

Extrai dados de uma tabela HTML `<table>`. Usa os headers como chaves.

```python
dados = await browser.extract_table(selector)
```

### Parametros

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| `selector` | `str` | — | Seletor da `<table>` |
| `next_page` | `str` | `None` | Seletor do botao de proxima pagina |
| `max_pages` | `int` | `100` | Maximo de paginas |

### Retorno

```python
[
    {"Nome": "Joao", "CPF": "123.456.789-00", "Saldo": "1.200,00"},
    {"Nome": "Maria", "CPF": "987.654.321-00", "Saldo": "3.500,00"},
]
```

### Exemplo

```python
# Tabela simples
clientes = await browser.extract_table("#tabela-clientes")

# Com paginacao
clientes = await browser.extract_table(
    "#tabela-clientes",
    next_page="#btn-proxima",
    max_pages=10,
)

# Converter pra DataFrame
import pandas as pd
df = pd.DataFrame(clientes)
```
