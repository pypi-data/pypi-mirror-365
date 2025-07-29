import click
import os
import shutil
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "templates"

@click.group()
def main():
    """GenAI Colosseum CLI"""
    pass

@main.command()
def list():
    """List available GenAI project templates"""
    templates = [f.name for f in TEMPLATE_DIR.iterdir() if f.is_dir()]
    click.echo("Available templates:")
    for t in templates:
        click.echo(f" - {t}")

@main.command()
@click.argument("template_name")
def install(template_name):
    """Install a template into the current directory"""
    src = TEMPLATE_DIR / template_name
    dest = Path.cwd() / template_name

    if not src.exists():
        click.echo(f"❌ Template '{template_name}' not found.")
        return

    if dest.exists():
        click.echo(f"⚠️ Folder '{template_name}' already exists in current directory.")
        return

    shutil.copytree(src, dest)
    click.echo(f"✅ Template '{template_name}' installed to '{dest}'.")
