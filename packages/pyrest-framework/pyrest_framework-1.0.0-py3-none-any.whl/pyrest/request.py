"""
Módulo Request do PYREST-FRAMEWORK
Contém a classe Request que representa uma requisição HTTP
"""

import json
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any, Optional

class Request:
    """Classe que representa a requisição HTTP"""
    
    def __init__(self, method: str, path: str, headers: Dict, body: str = ""):
        self.method = method.upper()
        self.path = path
        self.headers = {k.lower(): v for k, v in headers.items()}  # Headers em lowercase
        self.body = body
        self.params = {}  # Para parâmetros de rota (:id)
        self.query = {}   # Para query parameters (?name=value)
        self.json_data = None
        self.form_data = {}
        
        # Parse da URL e query parameters
        self._parse_url()
        
        # Parse do corpo da requisição
        self._parse_body()
    
    def _parse_url(self):
        """Faz o parse da URL e extrai query parameters"""
        parsed_url = urlparse(self.path)
        
        # Atualiza path sem query string
        self.path_without_query = parsed_url.path
        
        # Parse query parameters
        if parsed_url.query:
            self.query = {k: v[0] if len(v) == 1 else v 
                         for k, v in parse_qs(parsed_url.query).items()}
    
    def _parse_body(self):
        """Faz o parse do corpo da requisição baseado no Content-Type"""
        if not self.body:
            return
        
        content_type = self.headers.get('content-type', '').lower()
        
        # JSON
        if 'application/json' in content_type:
            try:
                self.json_data = json.loads(self.body)
            except json.JSONDecodeError:
                self.json_data = None
        
        # Form URL Encoded
        elif 'application/x-www-form-urlencoded' in content_type:
            try:
                self.form_data = {k: v[0] if len(v) == 1 else v 
                                for k, v in parse_qs(self.body).items()}
            except:
                self.form_data = {}
        
        # Multipart (básico - apenas para compatibilidade)
        elif 'multipart/form-data' in content_type:
            # Implementação básica - não suporta upload de arquivos
            self.form_data = {}
    
    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Obtém um header da requisição (case-insensitive)
        
        Args:
            name (str): Nome do header
            default (Optional[str]): Valor padrão se header não existir
        
        Returns:
            Optional[str]: Valor do header ou default
        """
        return self.headers.get(name.lower(), default)
    
    def get_query(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Obtém um query parameter
        
        Args:
            name (str): Nome do parâmetro
            default (Optional[str]): Valor padrão se parâmetro não existir
        
        Returns:
            Optional[str]: Valor do parâmetro ou default
        """
        return self.query.get(name, default)
    
    def get_param(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Obtém um parâmetro de rota
        
        Args:
            name (str): Nome do parâmetro
            default (Optional[str]): Valor padrão se parâmetro não existir
        
        Returns:
            Optional[str]: Valor do parâmetro ou default
        """
        return self.params.get(name, default)
    
    def get_json(self, key: str = None, default: Any = None) -> Any:
        """
        Obtém dados JSON da requisição
        
        Args:
            key (str, optional): Chave específica do JSON
            default (Any): Valor padrão se chave não existir
        
        Returns:
            Any: Dados JSON ou valor específico
        """
        if self.json_data is None:
            return default
        
        if key is None:
            return self.json_data
        
        return self.json_data.get(key, default)
    
    def get_form(self, key: str = None, default: Any = None) -> Any:
        """
        Obtém dados de formulário
        
        Args:
            key (str, optional): Chave específica do formulário
            default (Any): Valor padrão se chave não existir
        
        Returns:
            Any: Dados do formulário ou valor específico
        """
        if key is None:
            return self.form_data
        
        return self.form_data.get(key, default)
    
    def is_json(self) -> bool:
        """
        Verifica se a requisição contém JSON válido
        
        Returns:
            bool: True se contém JSON válido
        """
        return self.json_data is not None
    
    def is_form(self) -> bool:
        """
        Verifica se a requisição contém dados de formulário
        
        Returns:
            bool: True se contém dados de formulário
        """
        return bool(self.form_data)
    
    def is_secure(self) -> bool:
        """
        Verifica se a requisição é HTTPS
        
        Returns:
            bool: True se é HTTPS
        """
        # Verifica headers comuns de proxy/load balancer
        forwarded_proto = self.get_header('x-forwarded-proto')
        if forwarded_proto:
            return forwarded_proto.lower() == 'https'
        
        # Outros headers comuns
        if self.get_header('x-forwarded-ssl') == 'on':
            return True
        
        if self.get_header('x-url-scheme') == 'https':
            return True
        
        # Por padrão, assume HTTP (já que usamos HTTPServer)
        return False
    
    def get_user_agent(self) -> Optional[str]:
        """
        Obtém o User-Agent da requisição
        
        Returns:
            Optional[str]: User-Agent ou None
        """
        return self.get_header('user-agent')
    
    def get_content_type(self) -> Optional[str]:
        """
        Obtém o Content-Type da requisição
        
        Returns:
            Optional[str]: Content-Type ou None
        """
        return self.get_header('content-type')
    
    def get_content_length(self) -> int:
        """
        Obtém o Content-Length da requisição
        
        Returns:
            int: Content-Length ou 0
        """
        try:
            return int(self.get_header('content-length', '0'))
        except (ValueError, TypeError):
            return 0
    
    def get_remote_addr(self) -> Optional[str]:
        """
        Obtém o endereço IP do cliente
        
        Returns:
            Optional[str]: IP do cliente ou None
        """
        # Verifica headers de proxy
        forwarded_for = self.get_header('x-forwarded-for')
        if forwarded_for:
            # Pega o primeiro IP da lista
            return forwarded_for.split(',')[0].strip()
        
        real_ip = self.get_header('x-real-ip')
        if real_ip:
            return real_ip
        
        # Fallback (não disponível com HTTPServer básico)
        return None
    
    def accepts(self, content_type: str) -> bool:
        """
        Verifica se o cliente aceita um tipo de conteúdo
        
        Args:
            content_type (str): Tipo de conteúdo a verificar
        
        Returns:
            bool: True se aceita o tipo de conteúdo
        """
        accept_header = self.get_header('accept', '')
        if not accept_header:
            return True  # Se não especifica, aceita tudo
        
        return content_type.lower() in accept_header.lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a requisição para dicionário (útil para debugging)
        
        Returns:
            Dict[str, Any]: Dicionário com dados da requisição
        """
        return {
            'method': self.method,
            'path': self.path,
            'path_without_query': getattr(self, 'path_without_query', self.path),
            'headers': dict(self.headers),
            'params': dict(self.params),
            'query': dict(self.query),
            'json_data': self.json_data,
            'form_data': dict(self.form_data),
            'body_length': len(self.body),
            'content_type': self.get_content_type(),
            'user_agent': self.get_user_agent(),
            'is_json': self.is_json(),
            'is_form': self.is_form(),
            'is_secure': self.is_secure()
        }
    
    def __str__(self) -> str:
        """Representação string da requisição"""
        return f"<Request {self.method} {self.path}>"
    
    def __repr__(self) -> str:
        """Representação detalhada da requisição"""
        return (f"Request(method='{self.method}', path='{self.path}', "
                f"headers={len(self.headers)}, params={len(self.params)}, "
                f"query={len(self.query)})")