import sys
import os

# Añadir el directorio actual al path para resolver 'manager' correctamente
sys.path.insert(0, os.path.dirname(__file__))

from manager.agent import root_agent

__all__ = ["root_agent"]
