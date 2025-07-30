import click
import sys
from pathlib import Path
from tai_sql.generators import BaseGenerator, ModelsGenerator, CRUDGenerator, ERDiagramGenerator
from tai_api.generators import RoutersGenerator

from tai_api import ProjectConfig


def run_generate(config: ProjectConfig, schema_name: str):
    """Run the configured generators."""
    # Ejecutar cada generador
    click.echo("🚀 Ejecutando generadores...")
    click.echo()
    
    # Construir los directorios de salida de forma robusta usando namespace y subnamespace
    base_path = Path(config.namespace) / config.subnamespace
    database_path = base_path / "database"
    diagrams_path = base_path / "diagrams"
    database_resources_path = Path(config.subnamespace) / "database"

    models_generator = ModelsGenerator(database_path.as_posix())
    crud_generator = CRUDGenerator(
        output_dir=database_path.as_posix(),
        models_import_path=f"{config.subnamespace}.database.{schema_name}.models",
        mode='async'
    )
    er_generator = ERDiagramGenerator(diagrams_path.as_posix())
    
    
    endpoints_generator = RoutersGenerator(
        output_dir=str(base_path / "routers" / "generated"), 
        database_resources_path=database_resources_path.as_posix()
    )

    generators: list[BaseGenerator] = [
        models_generator,
        crud_generator,
        er_generator,
        endpoints_generator
    ]

    for generator in generators:
        try:
            generator_name = generator.__class__.__name__
            click.echo(f"Ejecutando: {click.style(generator_name, bold=True)}")
            
            # El generador se encargará de descubrir los modelos internamente
            result = generator.generate()
            
            click.echo(f"✅ Generador {generator_name} completado con éxito.")
            if result:
                click.echo(f"   Recursos en: {result}")
        except Exception as e:
            click.echo(f"❌ Error al ejecutar el generador {generator_name}: {str(e)}", err=True)
            sys.exit(1)
        
        finally:
            click.echo()