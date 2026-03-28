"""PyWebFlx CLI — install extension and check connection.

Commands:
    pywebflx install-extension  — Install Chrome extension (copies to clipboard + opens Chrome)
    pywebflx check              — Verify extension is connected
    pywebflx uninstall-extension — Remove extension

Example:
    $ pip install pywebflx
    $ pywebflx install-extension
    $ pywebflx check
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

import click

from pywebflx import __version__


def _get_extension_dir() -> Path:
    """Get the path to the bundled Chrome extension directory."""
    # Inside installed package: src/pywebflx/extension/
    pkg_ext = Path(__file__).resolve().parent / "extension"
    if pkg_ext.exists() and (pkg_ext / "manifest.json").exists():
        return pkg_ext
    # Development: repo root extension/
    dev_ext = Path(__file__).resolve().parent.parent.parent / "extension"
    if dev_ext.exists() and (dev_ext / "manifest.json").exists():
        return dev_ext
    return pkg_ext


def _copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard (Windows/Mac/Linux)."""
    try:
        if sys.platform == "win32":
            process = subprocess.Popen(
                ["clip"], stdin=subprocess.PIPE, shell=True,
            )
            process.communicate(text.encode("utf-16le"))
            return True
        elif sys.platform == "darwin":
            process = subprocess.Popen(
                ["pbcopy"], stdin=subprocess.PIPE,
            )
            process.communicate(text.encode("utf-8"))
            return True
        else:
            process = subprocess.Popen(
                ["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE,
            )
            process.communicate(text.encode("utf-8"))
            return True
    except Exception:
        return False


def _open_chrome_extensions():
    """Open chrome://extensions in the browser."""
    try:
        if sys.platform == "win32":
            subprocess.Popen(["start", "chrome", "chrome://extensions"], shell=True)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Google Chrome", "chrome://extensions"])
        else:
            subprocess.Popen(["google-chrome", "chrome://extensions"])
        return True
    except Exception:
        return False


@click.group()
@click.version_option(version=__version__, prog_name="pywebflx")
def main():
    """PyWebFlx — Browser automation for already-open Chrome pages."""
    pass


@main.command("install-extension")
def install_extension():
    """Install the PyWebFlx Chrome extension in Chrome."""
    ext_dir = _get_extension_dir()

    click.echo()
    click.echo("  PyWebFlx — Instalacao da Extensao Chrome")
    click.echo("  " + "-" * 45)
    click.echo()

    if not ext_dir.exists():
        click.echo("  [ERRO] Extensao nao encontrada.")
        click.echo("  Reinstale com: pip install pywebflx")
        return

    ext_path = str(ext_dir)

    click.echo("  [1/3] Abra o Chrome em: chrome://extensions")
    click.echo("        -> Ative o 'Modo do desenvolvedor' (canto superior direito)")
    click.echo()
    click.echo("  [2/3] Clique em 'Carregar sem compactacao' e cole este caminho:")
    click.echo()
    click.echo(f"        {ext_path}")
    click.echo()
    click.echo("  [3/3] Apos instalar, verifique com:")
    click.echo("        pywebflx check")

    # Try to open Chrome
    _open_chrome_extensions()

    click.echo()


@main.command("uninstall-extension")
def uninstall_extension():
    """Remove the PyWebFlx Chrome extension."""
    click.echo()
    click.echo("  Para remover a extensao:")
    click.echo("  1. Abra chrome://extensions")
    click.echo("  2. Encontre 'PyWebFlx Bridge'")
    click.echo("  3. Clique em 'Remover'")
    click.echo()

    _open_chrome_extensions()


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


@main.command("extension-path")
def extension_path():
    """Print the extension directory path (useful for scripts)."""
    ext_dir = _get_extension_dir()
    if ext_dir.exists():
        click.echo(str(ext_dir))
        _copy_to_clipboard(str(ext_dir))
    else:
        click.echo("Extension not found", err=True)
        sys.exit(1)
