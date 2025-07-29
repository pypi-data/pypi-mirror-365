"""
PYREST-FRAMEWORK
================

Framework Python para criação de APIs REST - Estilo Express.js
Desenvolvido para projetos acadêmicos.

Exemplo básico de uso:

    from pyrest import PyRest, Middlewares
    
    app = PyRest()
    
    @app.get('/')
    def home(req, res):
        res.json({"message": "Hello, PyRest!"})
    
    app.listen(3000)

Para mais exemplos e documentação completa, visite:
https://github.com/mamadusamadev/pyrest-framework
"""


__version__ = "1.0.0"
__author__ = "Mamadu Sama"
__email__ = "mamadusama19@gmail.com" 
__license__ = "MIT"
__description__ = "Framework Python para criação de APIs REST - Estilo Express.js"

# Importações principais
from .core import PyRestFramework as PyRest
from .middlewares import Middlewares
from .request import Request
from .response import Response
from .route import Route
from .utils import create_app
import os
# Aliases para compatibilidade
PyRestFramework = PyRest

# Exports principais
__all__ = [
    # Classes principais
    "PyRest",
    "PyRestFramework", 
    "Request",
    "Response", 
    "Route",
    "Middlewares",
    
    # Funções utilitárias
    "create_app",
    
    # Metadados
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
]

# Informações de versão
VERSION_INFO = tuple(map(int, __version__.split('.')))

def get_version():
    """Retorna a versão atual do framework"""
    return __version__

def get_info():
    """Retorna informações sobre o framework"""
    return {
        "name": "PYREST-FRAMEWORK",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "description": __description__,
        "python_requires": ">=3.7",
        "homepage": "https://github.com/seuusuario/pyrest-framework"
    }

# Banner para quando framework é importado
def _print_banner():
    """Imprime banner do framework (apenas em modo debug)"""
    import os
    if os.environ.get('PYREST_DEBUG', '').lower() in ('1', 'true', 'yes'):
        print(f"""
╔══════════════════════════════════════╗
║   PYREST-FRAMEWORK v{__version__}    ║
║    Framework Python para APIs REST   ║
║         Desenvolvido para            ║
╚══════════════════════════════════════╝
        """)

# Configurações globais
class Config:
    """Configurações globais do framework"""
    DEBUG = False
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 3000
    DEFAULT_CONTENT_TYPE = 'application/json'
    
    @classmethod
    def set_debug(cls, debug: bool):
        """Ativa/desativa modo debug"""
        cls.DEBUG = debug
        if debug:
            _print_banner()

# Importa banner se estiver em modo debug

if os.environ.get('PYREST_DEBUG', '').lower() in ('1', 'true', 'yes'):
    _print_banner()