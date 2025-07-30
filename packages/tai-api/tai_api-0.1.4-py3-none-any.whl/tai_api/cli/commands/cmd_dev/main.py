import sys
import click
import subprocess
from pathlib import Path

from tai_api import pm

@click.command()
def dev():
    """Inicia el servidor en modo desarrollo."""

    config = pm.get_project_config()

    if not config:
        click.echo("❌ No se encontró la configuración del proyecto. Asegúrate de haber inicializado el proyecto con tai-api init.", err=True)
        sys.exit(1)
    
    main_file = Path(config.namespace) / config.subnamespace / "__main__.py"

    sys.exit(subprocess.call(["fastapi", "dev", main_file.as_posix()]))