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

O comando vai mostrar o **caminho da extensão**. Depois:

1. Abra o Chrome e acesse `chrome://extensions`
2. Ative o **Modo do desenvolvedor** (botão no canto superior direito)
3. Clique em **Carregar sem compactação**
4. Cole o caminho mostrado pelo comando e confirme

!!! tip "Setup empresarial (múltiplas máquinas)"
    Os mesmos passos se aplicam para cada máquina. Após `pip install pywebflx`, a extensão já vem incluída no pacote — sem downloads adicionais.

## 3. Verificar

```bash
pywebflx check
```

Se aparecer "Extensão CONECTADA!", tudo está pronto.

## Comandos CLI

| Comando | Descrição |
|---------|-----------|
| `pywebflx install-extension` | Mostra o caminho da extensão para instalação |
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
