"""PyWebFlx CLI — install extension and check connection.

Commands:
    pywebflx install-extension  — Install Chrome extension automatically (Windows registry)
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

if sys.platform == "win32":
    import winreg

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


def _get_extension_id(ext_dir: Path) -> str:
    """Generate a stable extension ID from the path (for registry install)."""
    import hashlib
    # Chrome uses first 32 chars of hex(sha256(path)) mapped to a-p
    path_bytes = str(ext_dir).encode("utf-8")
    digest = hashlib.sha256(path_bytes).hexdigest()[:32]
    return "".join(chr(ord("a") + int(c, 16)) for c in digest)


def _install_registry(ext_dir: Path) -> bool:
    """Install extension via Windows Registry (Developer mode required)."""
    ext_id = _get_extension_id(ext_dir)
    ext_path = str(ext_dir)

    try:
        # Write to HKCU (no admin needed)
        # Chrome reads extensions from this registry path
        reg_path = r"SOFTWARE\Google\Chrome\Extensions\\" + ext_id
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "path", 0, winreg.REG_SZ, ext_path)
        winreg.SetValueEx(key, "version", 0, winreg.REG_SZ, "1.0.0")
        winreg.CloseKey(key)
        return True
    except Exception as e:
        click.echo(f"  Registry write failed: {e}")
        return False


def _uninstall_registry(ext_dir: Path) -> bool:
    """Remove extension registry entry."""
    ext_id = _get_extension_id(ext_dir)
    try:
        reg_path = r"SOFTWARE\Google\Chrome\Extensions\\" + ext_id
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
        return True
    except FileNotFoundError:
        return True
    except Exception:
        return False


@click.group()
@click.version_option(version=__version__, prog_name="pywebflx")
def main():
    """PyWebFlx — Browser automation for already-open Chrome pages."""
    pass


@main.command("install-extension")
@click.option("--manual", is_flag=True, help="Show manual installation steps instead")
def install_extension(manual: bool):
    """Install the PyWebFlx Chrome extension."""
    ext_dir = _get_extension_dir()

    click.echo("=" * 60)
    click.echo("  PyWebFlx — Chrome Extension Installation")
    click.echo("=" * 60)
    click.echo()

    if not ext_dir.exists():
        click.echo(f"Extension NOT found at: {ext_dir}")
        click.echo("Please reinstall pywebflx or check your installation.")
        return

    click.echo(f"Extension found at: {ext_dir}")
    click.echo()

    if manual or sys.platform != "win32":
        _show_manual_steps(ext_dir)
        return

    # Windows automatic install via registry
    click.echo("Installing via Windows Registry...")
    click.echo()

    if _install_registry(ext_dir):
        click.echo("  Registry entry created successfully!")
        click.echo()
        click.echo("Next steps:")
        click.echo("  1. Open Chrome and go to: chrome://extensions")
        click.echo("  2. Enable 'Developer mode' (toggle in top-right)")
        click.echo("  3. The extension 'PyWebFlx Bridge' should appear automatically")
        click.echo("  4. If not, click 'Load unpacked' and select:")
        click.echo(f"     {ext_dir}")
        click.echo()

        try:
            subprocess.Popen(
                ["start", "chrome", "chrome://extensions"],
                shell=True,
            )
            click.echo("Opening chrome://extensions...")
        except Exception:
            pass
    else:
        click.echo("  Automatic install failed. Falling back to manual steps:")
        click.echo()
        _show_manual_steps(ext_dir)

    click.echo()
    click.echo("After installing, run 'pywebflx check' to verify the connection.")


@main.command("uninstall-extension")
def uninstall_extension():
    """Remove the PyWebFlx Chrome extension registry entry."""
    ext_dir = _get_extension_dir()

    if sys.platform == "win32":
        if _uninstall_registry(ext_dir):
            click.echo("Extension registry entry removed.")
            click.echo("You may also need to remove it from chrome://extensions manually.")
        else:
            click.echo("Could not remove registry entry.")
    else:
        click.echo("Remove the extension from chrome://extensions manually.")


def _show_manual_steps(ext_dir: Path):
    """Show manual installation instructions."""
    click.echo("Follow these steps to install:")
    click.echo()
    click.echo("  1. Open Chrome and go to: chrome://extensions")
    click.echo("  2. Enable 'Developer mode' (toggle in top-right corner)")
    click.echo("  3. Click 'Load unpacked'")
    click.echo(f"  4. Select this folder: {ext_dir}")
    click.echo("  5. The extension 'PyWebFlx Bridge' should appear")

    try:
        if sys.platform == "win32":
            subprocess.Popen(["start", "chrome", "chrome://extensions"], shell=True)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Google Chrome", "chrome://extensions"])
    except Exception:
        pass


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
