# inspect

Retorna uma visao resumida da estrutura do DOM, otimizada para consumo por IAs e debug rapido.

Usa **~95% menos tokens** que o HTML bruto, mantendo a informacao util.

## Assinatura

```python
estrutura = await browser.inspect(selector="", depth=2, samples=2)
```

## Parametros

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| `selector` | `str` | `""` | Escopo (vazio = pagina inteira) |
| `depth` | `int` | `2` | Profundidade maxima de travessia |
| `samples` | `int` | `2` | Amostras de dados em listas/tabelas |

## Exemplo de saida

```
<body>
  <header#top-nav .navbar>
    <button.btn-menu> "Menu"
    <input#search type="search" placeholder="Buscar...">
    <a.logo> "Portal Sicoob"
  <main#content>
    <form#login-form>
      <input#usuario type="text" placeholder="Usuario" [required]>
      <input#senha type="password" placeholder="Senha" [required]>
      <select#agencia> 3 options: ["0001 - Centro", "0032 - Belem"]
      <button#btn-login type="submit"> "Entrar"
    <div.avisos>
      <table#tabela-avisos> 3 cols x 12 rows
        headers: ["Data", "Tipo", "Mensagem"]
        sample[0]: ["28/03", "Info", "Manutencao programada"]
```

## Fluxo de uso

### 1. Inspect geral — entender a pagina

```python
estrutura = await browser.inspect(depth=5, samples=2)
print(estrutura)
```

Resultado:
```
<div.quote> x 10 items
  sample[0]: "The world as we have created it..."
```

### 2. Inspect focado — ver dentro de um elemento

```python
detalhe = await browser.inspect(".quote", depth=5)
print(detalhe)
```

Resultado:
```
<div.quote>
  <span.text> "The world as we have created it..."
  <span>
    <small.author> "Albert Einstein"
  <div.tags>
    <a.tag> x 3 items
      sample[0]: "change"
```

### 3. Usar os seletores descobertos

```python
quotes = await browser.extract_data(
    container="body",
    row=".quote",
    columns={"texto": ".text", "autor": ".author"}
)
```

## O que o inspect mostra

| Elemento | Como aparece |
|----------|-------------|
| IDs e classes | `<div#login-form.container>` |
| Inputs | `<input#email type="text" placeholder="Email" [required]>` |
| Links | `<a.logo href="/home">` |
| Texto | `<button> "Entrar"` |
| Tabelas | `<table> 3 cols x 12 rows` + headers + samples |
| Selects | `<select> 5 options: ["Op1", "Op2", ...]` |
| Listas | `<div.card> x 20 items` + samples |

## Quando usar

| Cenario | Comando |
|---------|---------|
| Entender pagina desconhecida | `inspect(depth=5)` |
| Encontrar seletores para automacao | `inspect(".container", depth=5)` |
| Alimentar IA com contexto da pagina | `inspect(depth=3, samples=2)` |
| Debug rapido sem DevTools | `inspect()` |
