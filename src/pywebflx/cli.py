"""PyWebFlx CLI.

Commands:
    pywebflx install-extension  — Show extension installation steps
    pywebflx check              — Verify extension is connected
    pywebflx docs               — Show documentation links

Example:
    $ pip install pywebflx
    $ pywebflx install-extension
    $ pywebflx check
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click

from pywebflx import __version__

DOCS_URL = "https://theflexa.github.io/pywebflx/"
REPO_URL = "https://github.com/theflexa/pywebflx"


def _get_extension_dir() -> Path:
    """Get the path to the bundled Chrome extension directory."""
    pkg_ext = Path(__file__).resolve().parent / "extension"
    if pkg_ext.exists() and (pkg_ext / "manifest.json").exists():
        return pkg_ext
    dev_ext = Path(__file__).resolve().parent.parent.parent / "extension"
    if dev_ext.exists() and (dev_ext / "manifest.json").exists():
        return dev_ext
    return pkg_ext


@click.group()
@click.version_option(version=__version__, prog_name="pywebflx")
def main():
    """PyWebFlx — Browser automation for already-open Chrome pages."""
    pass


@main.command("install-extension")
def install_extension():
    """Show steps to install the Chrome extension."""
    ext_dir = _get_extension_dir()

    click.echo()
    click.echo("  PyWebFlx — Instalacao da Extensao Chrome")
    click.echo("  " + "-" * 45)
    click.echo()

    if not ext_dir.exists():
        click.echo("  [ERRO] Extensao nao encontrada.")
        click.echo("  Reinstale com: pip install pywebflx")
        return

    click.echo("  [1/3] Abra o Chrome e acesse: chrome://extensions")
    click.echo("        Ative o 'Modo do desenvolvedor' (canto superior direito)")
    click.echo()
    click.echo("  [2/3] Clique em 'Carregar sem compactacao' e cole este caminho:")
    click.echo()
    click.echo(f"        {ext_dir}")
    click.echo()
    click.echo("  [3/3] Apos instalar, verifique com: pywebflx check")
    click.echo()
    click.echo(f"  Documentacao: {DOCS_URL}")
    click.echo()


@main.command("uninstall-extension")
def uninstall_extension():
    """Show steps to remove the Chrome extension."""
    click.echo()
    click.echo("  Para remover a extensao:")
    click.echo("  1. Abra chrome://extensions")
    click.echo("  2. Encontre 'PyWebFlx Bridge'")
    click.echo("  3. Clique em 'Remover'")
    click.echo()


@main.command("check")
def check():
    """Check if the Chrome extension is connected."""
    click.echo()
    click.echo("  Verificando conexao com a extensao...")
    click.echo()

    async def _check():
        from pywebflx.connection import WebSocketServer
        from pywebflx.exceptions import ExtensionNotConnectedError

        server = WebSocketServer(port=9819)
        await server.start()
        try:
            await server.wait_for_connection(timeout=5)
            click.echo("  [OK] Extensao CONECTADA!")
            click.echo("  PyWebFlx esta pronto para uso.")
            return True
        except ExtensionNotConnectedError:
            click.echo("  [ERRO] Extensao NAO conectada.")
            click.echo()
            click.echo("  Verifique:")
            click.echo("  1. Chrome esta aberto?")
            click.echo("  2. Extensao 'PyWebFlx Bridge' esta instalada e ativada?")
            click.echo("  3. Nenhum outro script pywebflx esta rodando na porta 9819?")
            return False
        finally:
            await server.stop()

    connected = asyncio.run(_check())
    click.echo()
    if not connected:
        sys.exit(1)


@main.command("docs")
def docs():
    """Show documentation and repository links."""
    click.echo()
    click.echo("  PyWebFlx — Documentacao")
    click.echo("  " + "-" * 45)
    click.echo()
    click.echo(f"  Site:       {DOCS_URL}")
    click.echo(f"  GitHub:     {REPO_URL}")
    click.echo(f"  Versao:     {__version__}")
    click.echo()
    click.echo("  Comandos disponiveis:")
    click.echo("    pywebflx install-extension   Instalar extensao do Chrome")
    click.echo("    pywebflx check               Verificar conexao")
    click.echo("    pywebflx docs                Este menu")
    click.echo("    pywebflx --version           Versao instalada")
    click.echo()


@main.command("extension-path")
def extension_path():
    """Print the extension directory path (useful for scripts)."""
    ext_dir = _get_extension_dir()
    if ext_dir.exists():
        click.echo(str(ext_dir))
    else:
        click.echo("Extension not found", err=True)
        sys.exit(1)
