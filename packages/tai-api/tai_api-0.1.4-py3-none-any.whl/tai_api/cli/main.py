import click
from .commands import (
    generate,
    init,
    dev
)

@click.group()
def cli():
    """CLI para tai-api: Un framework para APIs basado en FastAPI."""
    pass

cli.add_command(generate)
cli.add_command(init)
cli.add_command(dev)

if __name__ == '__main__':
    cli()