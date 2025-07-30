# src/e23data/__init__.py

# Importa as funções principais do módulo client.py para o namespace do pacote e23data
from .client import get_density, get_viscosity, get_all_properties, get_property_info, E23DataClient

# Opcional: Define __all__ para especificar o que é importado com 'from e23data import *'
__all__ = [
    "get_density",
    "get_viscosity",
    "get_all_properties",
    "get_property_info",
    "E23DataClient", # Se você quiser expor a classe cliente também
]

# Opcional: Define a versão do pacote aqui ou no pyproject.toml
# Se já está no pyproject.toml, não precisa duplicar aqui.
# __version__ = "0.0.1"
    