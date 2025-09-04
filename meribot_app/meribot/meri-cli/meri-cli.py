#!/usr/bin/env python3
"""
Punto de entrada principal para meri-cli.
Permite ejecutar el CLI directamente desde el directorio meri-cli.
"""

import sys
import os

# Agregar el directorio padre al path para importar meribot
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Importar el módulo CLI
from main import cli

if __name__ == '__main__':
    cli()
