"""
Módulo Response do PYREST-FRAMEWORK
Contém a classe Response que representa uma resposta HTTP
"""

import json
from typing import Any, Dict, Optional, Union

class Response:
    """Classe que representa a resposta HTTP"""
    
    def __init__(self):
        self.status_code = 200
        self.headers = {'Content-Type': 'application/json'}
        self.body = ""
        self._sent = False
    
    def status(self, code: int):
        """
        Define o status code da resposta
        
        Args:
            code (int): Código de status HTTP
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.status_code = code
        return self
    
    def header(self, key: str, value: str):
        """
        Define um header da resposta
        
        Args:
            key (str): Nome do header
            value (str): Valor do header
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.headers[key] = value
        return self
    
    def headers_dict(self, headers: Dict[str, str]):
        """
        Define múltiplos headers de uma vez
        
        Args:
            headers (Dict[str, str]): Dicionário com headers
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.headers.update(headers)
        return self
    
    def json(self, data: Any, indent: int = None, ensure_ascii: bool = False):
        """
        Envia resposta em JSON
        
        Args:
            data (Any): Dados para serializar em JSON
            indent (int, optional): Indentação do JSON
            ensure_ascii (bool): Se deve escapar caracteres não-ASCII
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.headers['Content-Type'] = 'application/json; charset=utf-8'
        
        try:
            self.body = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
        except (TypeError, ValueError) as e:
            # Se falhar na serialização, retorna erro
            error_data = {
                "error": "JSON Serialization Error",
                "message": str(e)
            }
            self.body = json.dumps(error_data, ensure_ascii=False)
            self.status_code = 500
        
        self._sent = True
        return self
    
    def send(self, data: Union[str, bytes, int, float, bool]):
        """
        Envia resposta em texto plano
        
        Args:
            data: Dados para enviar
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.headers['Content-Type'] = 'text/plain; charset=utf-8'
        self.body = str(data)
        self._sent = True
        return self
    
    def html(self, html_content: str):
        """
        Envia resposta em HTML
        
        Args:
            html_content (str): Conteúdo HTML
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.body = html_content
        self._sent = True
        return self
    
    def xml(self, xml_content: str):
        """
        Envia resposta em XML
        
        Args:
            xml_content (str): Conteúdo XML
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.headers['Content-Type'] = 'application/xml; charset=utf-8'
        self.body = xml_content
        self._sent = True
        return self
    
    def file(self, content: bytes, filename: str, mimetype: str = None):
        """
        Envia arquivo como resposta
        
        Args:
            content (bytes): Conteúdo do arquivo
            filename (str): Nome do arquivo
            mimetype (str, optional): Tipo MIME do arquivo
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        if mimetype:
            self.headers['Content-Type'] = mimetype
        else:
            # Detecta tipo MIME básico baseado na extensão
            if filename.endswith('.json'):
                self.headers['Content-Type'] = 'application/json'
            elif filename.endswith('.html'):
                self.headers['Content-Type'] = 'text/html'
            elif filename.endswith('.css'):
                self.headers['Content-Type'] = 'text/css'
            elif filename.endswith('.js'):
                self.headers['Content-Type'] = 'application/javascript'
            elif filename.endswith('.png'):
                self.headers['Content-Type'] = 'image/png'
            elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                self.headers['Content-Type'] = 'image/jpeg'
            elif filename.endswith('.pdf'):
                self.headers['Content-Type'] = 'application/pdf'
            elif filename.endswith('.zip'):
                self.headers['Content-Type'] = 'application/zip'
            else:
                self.headers['Content-Type'] = 'application/octet-stream'
        
        self.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        self.body = content.decode('utf-8', errors='ignore')  # Para compatibilidade
        self._sent = True
        return self
    
    def redirect(self, url: str, permanent: bool = False):
        """
        Redireciona para outra URL
        
        Args:
            url (str): URL de destino
            permanent (bool): Se é redirecionamento permanente (301) ou temporário (302)
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.status_code = 301 if permanent else 302
        self.headers['Location'] = url
        self.body = f'Redirecting to {url}'
        self._sent = True
        return self
    
    def cookie(self, name: str, value: str, max_age: int = None, 
               path: str = '/', domain: str = None, secure: bool = False, 
               httponly: bool = False, samesite: str = None):
        """
        Define um cookie na resposta
        
        Args:
            name (str): Nome do cookie
            value (str): Valor do cookie
            max_age (int, optional): Tempo de vida em segundos
            path (str): Caminho do cookie
            domain (str, optional): Domínio do cookie
            secure (bool): Se deve ser enviado apenas via HTTPS
            httponly (bool): Se deve ser acessível apenas via HTTP
            samesite (str, optional): Política SameSite ('Strict', 'Lax', 'None')
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        cookie_value = f"{name}={value}"
        
        if max_age is not None:
            cookie_value += f"; Max-Age={max_age}"
        
        cookie_value += f"; Path={path}"
        
        if domain:
            cookie_value += f"; Domain={domain}"
        
        if secure:
            cookie_value += "; Secure"
        
        if httponly:
            cookie_value += "; HttpOnly"
        
        if samesite:
            cookie_value += f"; SameSite={samesite}"
        
        # Adiciona cookie aos headers (permite múltiplos cookies)
        if 'Set-Cookie' in self.headers:
            # Se já existe um cookie, transforma em lista
            existing = self.headers['Set-Cookie']
            if isinstance(existing, str):
                self.headers['Set-Cookie'] = [existing, cookie_value]
            else:
                existing.append(cookie_value)
        else:
            self.headers['Set-Cookie'] = cookie_value
        
        return self
    
    def clear_cookie(self, name: str, path: str = '/', domain: str = None):
        """
        Remove um cookie definindo sua expiração no passado
        
        Args:
            name (str): Nome do cookie
            path (str): Caminho do cookie
            domain (str, optional): Domínio do cookie
        
        Returns:
            Response: Self para permitir method chaining
        """
        return self.cookie(name, '', max_age=0, path=path, domain=domain)
    
    def cors(self, origin: str = '*', methods: str = 'GET, POST, PUT, DELETE, OPTIONS',
             headers: str = 'Content-Type, Authorization', credentials: bool = False):
        """
        Configura headers CORS
        
        Args:
            origin (str): Origens permitidas
            methods (str): Métodos HTTP permitidos
            headers (str): Headers permitidos
            credentials (bool): Se permite envio de credenciais
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.headers['Access-Control-Allow-Origin'] = origin
        self.headers['Access-Control-Allow-Methods'] = methods
        self.headers['Access-Control-Allow-Headers'] = headers
        
        if credentials:
            self.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return self
    
    def cache_control(self, max_age: int = None, no_cache: bool = False, 
                     no_store: bool = False, public: bool = False, 
                     private: bool = False):
        """
        Define headers de controle de cache
        
        Args:
            max_age (int, optional): Tempo máximo de cache em segundos
            no_cache (bool): Se não deve usar cache
            no_store (bool): Se não deve armazenar
            public (bool): Se pode ser cacheado por proxies públicos
            private (bool): Se deve ser cacheado apenas pelo cliente
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        cache_parts = []
        
        if no_cache:
            cache_parts.append('no-cache')
        
        if no_store:
            cache_parts.append('no-store')
        
        if public:
            cache_parts.append('public')
        
        if private:
            cache_parts.append('private')
        
        if max_age is not None:
            cache_parts.append(f'max-age={max_age}')
        
        if cache_parts:
            self.headers['Cache-Control'] = ', '.join(cache_parts)
        
        return self
    
    def etag(self, value: str, weak: bool = False):
        """
        Define ETag para cache condicional
        
        Args:
            value (str): Valor do ETag
            weak (bool): Se é um ETag fraco
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        etag_value = f'W/"{value}"' if weak else f'"{value}"'
        self.headers['ETag'] = etag_value
        return self
    
    def last_modified(self, date: str):
        """
        Define header Last-Modified
        
        Args:
            date (str): Data em formato RFC 2822
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.headers['Last-Modified'] = date
        return self
    
    def content_encoding(self, encoding: str):
        """
        Define encoding do content (gzip, deflate, etc.)
        
        Args:
            encoding (str): Tipo de encoding
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.headers['Content-Encoding'] = encoding
        return self
    
    def security_headers(self, csp: str = None, xss_protection: bool = True,
                        content_type_options: bool = True, frame_options: str = 'DENY',
                        hsts: bool = False, hsts_max_age: int = 31536000):
        """
        Define headers de segurança comuns
        
        Args:
            csp (str, optional): Content Security Policy
            xss_protection (bool): Ativar X-XSS-Protection
            content_type_options (bool): Ativar X-Content-Type-Options
            frame_options (str): X-Frame-Options ('DENY', 'SAMEORIGIN', 'ALLOW-FROM uri')
            hsts (bool): Ativar HTTP Strict Transport Security
            hsts_max_age (int): Tempo em segundos para HSTS
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        if csp:
            self.headers['Content-Security-Policy'] = csp
        
        if xss_protection:
            self.headers['X-XSS-Protection'] = '1; mode=block'
        
        if content_type_options:
            self.headers['X-Content-Type-Options'] = 'nosniff'
        
        if frame_options:
            self.headers['X-Frame-Options'] = frame_options
        
        if hsts:
            self.headers['Strict-Transport-Security'] = f'max-age={hsts_max_age}; includeSubDomains'
        
        return self
    
    def get_content_length(self) -> int:
        """
        Obtém o tamanho do conteúdo
        
        Returns:
            int: Tamanho do corpo da resposta em bytes
        """
        return len(self.body.encode('utf-8'))
    
    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Obtém um header da resposta
        
        Args:
            name (str): Nome do header
            default (Optional[str]): Valor padrão se header não existir
        
        Returns:
            Optional[str]: Valor do header ou default
        """
        return self.headers.get(name, default)
    
    def remove_header(self, name: str):
        """
        Remove um header da resposta
        
        Args:
            name (str): Nome do header a remover
        
        Returns:
            Response: Self para permitir method chaining
        """
        if self._sent:
            return self
        
        self.headers.pop(name, None)
        return self
    
    def is_sent(self) -> bool:
        """
        Verifica se a resposta já foi enviada
        
        Returns:
            bool: True se já foi enviada
        """
        return self._sent
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a resposta para dicionário (útil para debugging)
        
        Returns:
            Dict[str, Any]: Dicionário com dados da resposta
        """
        return {
            'status_code': self.status_code,
            'headers': dict(self.headers),
            'body_length': len(self.body),
            'content_type': self.get_header('Content-Type'),
            'is_sent': self._sent
        }
    
    def __str__(self) -> str:
        """Representação string da resposta"""
        return f"<Response {self.status_code}>"
    
    def __repr__(self) -> str:
        """Representação detalhada da resposta"""
        return (f"Response(status_code={self.status_code}, "
                f"headers={len(self.headers)}, body_length={len(self.body)}, "
                f"is_sent={self._sent})")