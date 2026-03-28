# Instalação

## 1. Instalar a biblioteca

```bash
pip install pywebflx
```

Ou para desenvolvimento:

```bash
git clone https://github.com/theflexa/pywebflx.git
cd pywebflx
pip install -e ".[dev]"
```

## 2. Instalar a extensão do Chrome

```bash
pywebflx install-extension
```

O comando irá:

1. **Copiar** o caminho da extensão para a área de transferência automaticamente
2. **Abrir** o Chrome em `chrome://extensions`
3. Você só precisa:
    - Ativar o **Modo do desenvolvedor** (botão no canto superior direito)
    - Clicar em **Carregar sem compactação**
    - Colar o caminho (**Ctrl+V**) na barra de endereço e confirmar

!!! tip "Setup empresarial (múltiplas máquinas)"
    Os mesmos passos se aplicam para cada máquina. Após `pip install pywebflx`, a extensão já vem incluída no pacote — sem downloads adicionais.

## 3. Verificar

```bash
pywebflx check
```

Se aparecer "Extensão CONECTADA!", tudo está pronto.

## Outros comandos CLI

| Comando | Descrição |
|---------|-----------|
| `pywebflx install-extension` | Instala extensão Chrome (copia caminho + abre Chrome) |
| `pywebflx check` | Verifica conexão com a extensão |
| `pywebflx uninstall-extension` | Instruções para remover a extensão |
| `pywebflx extension-path` | Exibe o caminho da extensão (útil para scripts) |
| `pywebflx --version` | Mostra a versão instalada |

## Requisitos

- Python 3.10+
- Google Chrome
- Extensão PyWebFlx Bridge instalada

## Dependências

| Pacote | Uso |
|--------|-----|
| `websockets` | Comunicação Python <-> Extensão |
| `loguru` | Logging estruturado |
| `click` | CLI (install-extension, check) |
