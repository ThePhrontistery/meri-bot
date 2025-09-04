#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación MeriBot.

Este módulo proporciona la interfaz de línea de comandos principal
y el punto de entrada para la aplicación.
"""

import sys
import os
import importlib.util

# Cargar el módulo main.py desde meri-cli usando importlib
def load_cli_module():
    main_path = os.path.join(os.path.dirname(__file__), 'meri-cli', 'main.py')
    if not os.path.exists(main_path):
        print(f"Error: No se encontró el archivo CLI en {main_path}")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location("meri_cli_main", main_path)
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    return main_module

if __name__ == "__main__":
    main_module = load_cli_module()
    main_module.cli()
