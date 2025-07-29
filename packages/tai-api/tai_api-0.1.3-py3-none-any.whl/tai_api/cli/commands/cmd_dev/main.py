import sys
import click
import subprocess

@click.command()
def dev():
    """Inicia el servidor en modo desarrollo."""
    sys.exit(subprocess.call(["fastapi", "dev", "api/api/__main__.py"]))