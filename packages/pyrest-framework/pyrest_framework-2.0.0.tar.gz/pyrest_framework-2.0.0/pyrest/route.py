"""
Módulo Route do PYREST-FRAMEWORK
Contém a classe Route para gerenciamento de rotas
"""

import re
from typing import Dict, Callable

class Route:
    """Classe que representa uma rota HTTP"""
    
    def __init__(self, method: str, path: str, handler: Callable):
        self.method = method.upper()
        self.path = path
        self.handler = handler
        self.pattern = self._compile_pattern(path)
    
    def _compile_pattern(self, path: str) -> re.Pattern:
        """
        Compila o padrão da rota para matching
        
        Args:
            path (str): Caminho da rota (ex: '/users/:id')
        
        Returns:
            re.Pattern: Padrão compilado para matching
        """
        # Converte parâmetros de rota (:id) para grupos regex
        pattern = re.sub(r':(\w+)', r'(?P<\1>[^/]+)', path)
        # Escapa caracteres especiais exceto os que já foram processados
        pattern = re.escape(pattern)
        # Restaura os grupos de captura
        pattern = pattern.replace(r'\(\?P\<', '(?P<').replace(r'\>[^/]\+\)', '>[^/]+)')
        return re.compile(f'^{pattern}$')
    
    def matches(self, method: str, path: str) -> bool:
        """
        Verifica se a rota corresponde ao método e caminho
        
        Args:
            method (str): Método HTTP
            path (str): Caminho da requisição
        
        Returns:
            bool: True se corresponde
        """
        if self.method != method.upper():
            return False
        
        return bool(self.pattern.match(path))
    
    def extract_params(self, path: str) -> Dict[str, str]:
        """
        Extrai parâmetros da URL baseado no padrão da rota
        
        Args:
            path (str): Caminho da requisição
        
        Returns:
            Dict[str, str]: Parâmetros extraídos
        """
        match = self.pattern.match(path)
        if match:
            return match.groupdict()
        return {}
    
    def __str__(self) -> str:
        """Representação string da rota"""
        return f"<Route {self.method} {self.path}>"
    
    def __repr__(self) -> str:
        """Representação detalhada da rota"""
        return f"Route(method='{self.method}', path='{self.path}', handler={self.handler.__name__})"
