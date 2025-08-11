#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación MeriBot.

Este módulo proporciona la interfaz de línea de comandos principal
y el punto de entrada para la aplicación.
"""

import click
from meribot.cli.main import cli as meribot_cli

@click.group()
def cli():
    """Interfaz de línea de comandos para MeriBot."""
    pass

# Añadir comandos del CLI
cli.add_command(meribot_cli)

if __name__ == "__main__":
    cli()
