import sys
import click

from tai_sql import pm
from .funcs import run_generate

@click.command()
@click.option('--schema', '-s', help='Nombre del esquema')
def generate(schema: str=None):
    """Genera recursos para la API."""

    if schema:
        pm.set_current_schema(schema)
    
    else:
        config = pm.load_config()
        if config:
            pm.set_current_schema(config.default_schema)

    if not schema and not pm.db:
        click.echo(f"❌ No existe ningún esquema por defecto", err=True)
        click.echo(f"   Puedes definir uno con: tai-sql set-default-schema <nombre>", err=True)
        click.echo(f"   O usar la opción: --schema <nombre_esquema>", err=True)
        sys.exit(1)

    run_generate()