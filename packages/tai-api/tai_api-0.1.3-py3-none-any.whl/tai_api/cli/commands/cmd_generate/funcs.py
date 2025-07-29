import click
import sys
from tai_sql.generators import BaseGenerator, ModelsGenerator, CRUDGenerator, ERDiagramGenerator
from tai_api.generators.fastapi import EndpointsGenerator

def run_generate():
    """Run the configured generators."""
    # Ejecutar cada generador
    click.echo("🚀 Ejecutando generadores...")
    click.echo()
    
    models_generator = ModelsGenerator(output_dir="api/api/database")
    crud_generator = CRUDGenerator(output_dir="api/api/database", mode='async')
    er_generator = ERDiagramGenerator(output_dir="api/api/diagrams")
    endpoints_generator = EndpointsGenerator(output_dir="api/api/routers/generated", database_resources_path="api/database")

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