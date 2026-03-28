"""PyWebFlx CLI — install extension and check connection.

Commands:
    pywebflx install-extension  — Guide Chrome extension installation
    pywebflx check              — Verify extension is connected

Example:
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
    pkg_root = Path(__file__).resolve().parent.parent.parent
    ext_dir = pkg_root / "extension"
    if not ext_dir.exists():
        ext_dir = Path(__file__).resolve().parent / "extension"
    return ext_dir


@click.group()
@click.version_option(version=__version__, prog_name="pywebflx")
def main():
    """PyWebFlx — Browser automation for already-open Chrome pages."""
    pass


@main.command("install-extension")
def install_extension():
    """Guide installation of the PyWebFlx Chrome extension."""
    ext_dir = _get_extension_dir()

    click.echo("=" * 60)
    click.echo("  PyWebFlx — Chrome Extension Installation")
    click.echo("=" * 60)
    click.echo()

    if ext_dir.exists():
        click.echo(f"Extension found at: {ext_dir}")
    else:
        click.echo(f"Extension NOT found at: {ext_dir}")
        click.echo("Please reinstall pywebflx or check your installation.")
        return

    click.echo()
    click.echo("Follow these steps to install:")
    click.echo()
    click.echo("  1. Open Chrome and go to: chrome://extensions")
    click.echo("  2. Enable 'Developer mode' (toggle in top-right corner)")
    click.echo("  3. Click 'Load unpacked'")
    click.echo(f"  4. Select this folder: {ext_dir}")
    click.echo("  5. The extension 'PyWebFlx Bridge' should appear")
    click.echo()

    try:
        if sys.platform == "win32":
            subprocess.Popen(
                ["start", "chrome", "chrome://extensions"],
                shell=True,
            )
            click.echo("Opening chrome://extensions in your browser...")
        elif sys.platform == "darwin":
            subprocess.Popen(
                ["open", "-a", "Google Chrome", "chrome://extensions"],
            )
            click.echo("Opening chrome://extensions in your browser...")
    except Exception:
        click.echo("Could not open Chrome automatically. Please open chrome://extensions manually.")

    click.echo()
    click.echo("After installing, run 'pywebflx check' to verify the connection.")


@main.command("check")
def check():
    """Check if the Chrome extension is connected."""
    click.echo("Checking PyWebFlx extension connection...")
    click.echo()

    async def _check():
        from pywebflx.connection import WebSocketServer
        from pywebflx.exceptions import ExtensionNotConnectedError

        server = WebSocketServer(port=9819)
        await server.start()
        try:
            await server.wait_for_connection(timeout=5)
            click.echo("Extension is CONNECTED!")
            click.echo("PyWebFlx is ready to use.")
            return True
        except ExtensionNotConnectedError:
            click.echo("Extension is NOT connected.")
            click.echo()
            click.echo("Make sure:")
            click.echo("  1. Chrome is open")
            click.echo("  2. PyWebFlx Bridge extension is installed and enabled")
            click.echo("  3. No other pywebflx instance is running on port 9819")
            return False
        finally:
            await server.stop()

    connected = asyncio.run(_check())
    if not connected:
        sys.exit(1)
