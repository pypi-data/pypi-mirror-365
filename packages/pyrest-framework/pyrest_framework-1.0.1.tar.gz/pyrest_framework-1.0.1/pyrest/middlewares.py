"""
Módulo Middlewares do PYREST-FRAMEWORK
Contém middlewares comuns e utilitários
"""

import json
import time
from typing import Dict, List, Callable, Any
from .request import Request
from .response import Response

class Middlewares:
    """Classe com middlewares comuns"""
    
    @staticmethod
    def cors(origin: str = "*", methods: str = "GET, POST, PUT, DELETE, PATCH, OPTIONS",
             headers: str = "Content-Type, Authorization", credentials: bool = False):
        """
        Middleware CORS para permitir requisições cross-origin
        
        Args:
            origin (str): Origens permitidas
            methods (str): Métodos HTTP permitidos
            headers (str): Headers permitidos
            credentials (bool): Se permite envio de credenciais
        """
        def cors_middleware(req: Request, res: Response):
            res.header("Access-Control-Allow-Origin", origin)
            res.header("Access-Control-Allow-Methods", methods)
            res.header("Access-Control-Allow-Headers", headers)
            
            if credentials:
                res.header("Access-Control-Allow-Credentials", "true")
            
            # Para requisições OPTIONS (preflight)
            if req.method == "OPTIONS":
                res.status(200).send("")
                return False  # Para a execução aqui
        
        return cors_middleware
    
    @staticmethod
    def logger(format: str = "combined"):
        """
        Middleware de logging de requisições
        
        Args:
            format (str): Formato do log ('combined', 'common', 'dev')
        """
        def logger_middleware(req: Request, res: Response):
            start_time = time.time()
            
            # Executa a requisição
            # O tempo será calculado após a resposta
            
            # Log após a resposta (será chamado no final)
            def log_response():
                duration = time.time() - start_time
                
                if format == "dev":
                    print(f"{req.method} {req.path} - {res.status_code} - {duration:.3f}s")
                elif format == "common":
                    print(f'{req.get_header("x-forwarded-for", "-")} - - [{time.strftime("%d/%b/%Y:%H:%M:%S %z")}] '
                          f'"{req.method} {req.path} HTTP/1.1" {res.status_code} {len(res.body)}')
                else:  # combined
                    user_agent = req.get_header("user-agent", "-")
                    print(f'{req.get_header("x-forwarded-for", "-")} - - [{time.strftime("%d/%b/%Y:%H:%M:%S %z")}] '
                          f'"{req.method} {req.path} HTTP/1.1" {res.status_code} {len(res.body)} '
                          f'"{req.get_header("referer", "-")}" "{user_agent}"')
            
            # Adiciona função de log à resposta
            res._log_response = log_response
        
        return logger_middleware
    
    @staticmethod
    def body_parser():
        """
        Middleware para parsing automático do corpo da requisição
        """
        def body_parser_middleware(req: Request, res: Response):
            # O parsing já é feito na classe Request
            # Este middleware apenas garante que está disponível
            pass
        
        return body_parser_middleware
    
    @staticmethod
    def json_parser():
        """
        Middleware para parsing específico de JSON
        """
        def json_parser_middleware(req: Request, res: Response):
            content_type = req.get_header("content-type", "")
            
            if "application/json" in content_type and req.body:
                try:
                    req.json_data = json.loads(req.body)
                except json.JSONDecodeError:
                    res.status(400).json({
                        "error": "Invalid JSON",
                        "message": "O corpo da requisição não é um JSON válido"
                    })
                    return False
        
        return json_parser_middleware
    
    @staticmethod
    def urlencoded():
        """
        Middleware para parsing de dados URL-encoded
        """
        def urlencoded_middleware(req: Request, res: Response):
            content_type = req.get_header("content-type", "")
            
            if "application/x-www-form-urlencoded" in content_type and req.body:
                try:
                    from urllib.parse import parse_qs
                    req.form_data = {k: v[0] if len(v) == 1 else v 
                                   for k, v in parse_qs(req.body).items()}
                except Exception:
                    res.status(400).json({
                        "error": "Invalid form data",
                        "message": "Dados do formulário inválidos"
                    })
                    return False
        
        return urlencoded_middleware
    
    @staticmethod
    def static_files(directory: str, prefix: str = "/static"):
        """
        Middleware para servir arquivos estáticos
        
        Args:
            directory (str): Diretório com arquivos estáticos
            prefix (str): Prefixo da URL para arquivos estáticos
        """
        import os
        
        def static_middleware(req: Request, res: Response):
            if req.path.startswith(prefix):
                # Remove o prefixo do caminho
                file_path = req.path[len(prefix):]
                
                # Constrói o caminho completo do arquivo
                full_path = os.path.join(directory, file_path.lstrip('/'))
                
                # Verifica se o arquivo existe e está dentro do diretório
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    try:
                        with open(full_path, 'rb') as f:
                            content = f.read()
                        
                        # Detecta o tipo MIME
                        import mimetypes
                        mime_type, _ = mimetypes.guess_type(full_path)
                        if not mime_type:
                            mime_type = 'application/octet-stream'
                        
                        res.header("Content-Type", mime_type)
                        res.body = content.decode('utf-8', errors='ignore')
                        res._sent = True
                        return False  # Para a execução aqui
                    
                    except Exception as e:
                        res.status(500).json({
                            "error": "File read error",
                            "message": str(e)
                        })
                        return False
                else:
                    res.status(404).json({
                        "error": "File not found",
                        "message": f"Arquivo {file_path} não encontrado"
                    })
                    return False
        
        return static_middleware
    
    @staticmethod
    def rate_limit(max_requests: int = 100, window_ms: int = 60000):
        """
        Middleware básico de rate limiting
        
        Args:
            max_requests (int): Número máximo de requisições por janela
            window_ms (int): Janela de tempo em milissegundos
        """
        # Armazena requisições por IP
        requests_store = {}
        
        def rate_limit_middleware(req: Request, res: Response):
            client_ip = req.get_header("x-forwarded-for", "unknown")
            current_time = time.time() * 1000  # Converte para ms
            
            # Limpa requisições antigas
            if client_ip in requests_store:
                requests_store[client_ip] = [
                    req_time for req_time in requests_store[client_ip]
                    if current_time - req_time < window_ms
                ]
            else:
                requests_store[client_ip] = []
            
            # Verifica se excedeu o limite
            if len(requests_store[client_ip]) >= max_requests:
                res.status(429).json({
                    "error": "Too Many Requests",
                    "message": "Limite de requisições excedido"
                })
                return False
            
            # Adiciona requisição atual
            requests_store[client_ip].append(current_time)
        
        return rate_limit_middleware
    
    @staticmethod
    def auth_required():
        """
        Middleware para autenticação básica
        """
        def auth_middleware(req: Request, res: Response):
            auth_header = req.get_header("authorization")
            
            if not auth_header:
                res.status(401).json({
                    "error": "Unauthorized",
                    "message": "Header Authorization é obrigatório"
                })
                return False
            
            # Verifica se é Bearer token
            if not auth_header.startswith("Bearer "):
                res.status(401).json({
                    "error": "Unauthorized",
                    "message": "Token deve ser do tipo Bearer"
                })
                return False
            
            # Aqui você pode adicionar sua lógica de validação do token
            # Por exemplo, verificar JWT, etc.
            token = auth_header[7:]  # Remove "Bearer "
            
            if not token:
                res.status(401).json({
                    "error": "Unauthorized",
                    "message": "Token inválido"
                })
                return False
        
        return auth_middleware
    
    @staticmethod
    def error_handler():
        """
        Middleware para tratamento global de erros
        """
        def error_handler_middleware(req: Request, res: Response):
            try:
                # Continua a execução
                pass
            except Exception as e:
                res.status(500).json({
                    "error": "Internal Server Error",
                    "message": str(e)
                })
                return False
        
        return error_handler_middleware
    
    @staticmethod
    def security_headers():
        """
        Middleware para adicionar headers de segurança
        """
        def security_middleware(req: Request, res: Response):
            res.header("X-Content-Type-Options", "nosniff")
            res.header("X-Frame-Options", "DENY")
            res.header("X-XSS-Protection", "1; mode=block")
            res.header("Referrer-Policy", "strict-origin-when-cross-origin")
        
        return security_middleware
