#!/usr/bin/env python3
"""
Ejemplo de uso del EndpointsGenerator de tai-api.

Este script muestra cómo usar el EndpointsGenerator para generar automáticamente
endpoints REST para FastAPI basados en los modelos definidos en tai_sql.
"""

import sys
import os

from tai_api.generators.fastapi import EndpointsGenerator
from tai_sql import pm

def main():
    """
    Función principal que demuestra el uso del EndpointsGenerator.
    """
    print("🚀 Generando endpoints de FastAPI con tai-api...")
    config = pm.load_config()

    if config:
        pm.set_current_schema(config.default_schema)
    
    # Crear una instancia del generador
    generator = EndpointsGenerator()
    
    try:
        # Generar los endpoints
        generator.generate()
        print("\n✅ ¡Endpoints generados exitosamente!")
            
    except Exception as e:
        import logging
        logging.exception(e)
        print(f"❌ Error al generar endpoints: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
