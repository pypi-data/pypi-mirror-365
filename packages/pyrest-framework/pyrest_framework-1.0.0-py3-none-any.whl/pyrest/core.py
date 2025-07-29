"""
Core module do PYREST-FRAMEWORK
Contém a classe principal PyRestFramework
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Callable, Optional
from .request import Request
from .response import Response
from .route import Route

class PyRestFramework:
    """Classe principal do framework PYREST"""
    
    def __init__(self):
        self.routes: List[Route] = []
        self.middlewares: List[Callable] = []
        self.error_handlers: Dict[int, Callable] = {}
    
    def use(self, middleware: Callable):
        """Adiciona um middleware global"""
        self.middlewares.append(middleware)
        return self
    
    def get(self, path: str, handler: Callable = None):
        """Define rota GET - pode ser usado como decorator ou chamada direta"""
        if handler is None:
            # Uso como decorator: @app.get('/path')
            def decorator(func):
                self.routes.append(Route('GET', path, func))
                return func
            return decorator
        else:
            # Uso direto: app.get('/path', handler)
            self.routes.append(Route('GET', path, handler))
            return self
    
    def post(self, path: str, handler: Callable = None):
        """Define rota POST - pode ser usado como decorator ou chamada direta"""
        if handler is None:
            def decorator(func):
                self.routes.append(Route('POST', path, func))
                return func
            return decorator
        else:
            self.routes.append(Route('POST', path, handler))
            return self
    
    def put(self, path: str, handler: Callable = None):
        """Define rota PUT - pode ser usado como decorator ou chamada direta"""
        if handler is None:
            def decorator(func):
                self.routes.append(Route('PUT', path, func))
                return func
            return decorator
        else:
            self.routes.append(Route('PUT', path, handler))
            return self
    
    def delete(self, path: str, handler: Callable = None):
        """Define rota DELETE - pode ser usado como decorator ou chamada direta"""
        if handler is None:
            def decorator(func):
                self.routes.append(Route('DELETE', path, func))
                return func
            return decorator
        else:
            self.routes.append(Route('DELETE', path, handler))
            return self
    
    def patch(self, path: str, handler: Callable = None):
        """Define rota PATCH - pode ser usado como decorator ou chamada direta"""
        if handler is None:
            def decorator(func):
                self.routes.append(Route('PATCH', path, func))
                return func
            return decorator
        else:
            self.routes.append(Route('PATCH', path, handler))
            return self
    
    def options(self, path: str, handler: Callable = None):
        """Define rota OPTIONS - pode ser usado como decorator ou chamada direta"""
        if handler is None:
            def decorator(func):
                self.routes.append(Route('OPTIONS', path, func))
                return func
            return decorator
        else:
            self.routes.append(Route('OPTIONS', path, handler))
            return self
    
    def error_handler(self, status_code: int):
        """Decorator para definir handlers de erro personalizados"""
        def decorator(handler: Callable):
            self.error_handlers[status_code] = handler
            return handler
        return decorator
    
    def _find_route(self, method: str, path: str) -> Optional[Route]:
        """Encontra a rota correspondente"""
        for route in self.routes:
            if route.matches(method, path):
                return route
        return None
    
    def _execute_middlewares(self, req: Request, res: Response) -> bool:
        """Executa middlewares. Retorna False se algum middleware parar a execução"""
        for middleware in self.middlewares:
            try:
                result = middleware(req, res)
                # Se o middleware retornar False, para a execução
                if result is False:
                    return False
            except Exception as e:
                print(f"Erro no middleware: {e}")
                return False
        return True
    
    def _handle_error(self, status_code: int, req: Request, res: Response, message: str = ""):
        """Trata erros HTTP"""
        if status_code in self.error_handlers:
            try:
                self.error_handlers[status_code](req, res)
                return
            except Exception as e:
                print(f"Erro no handler de erro: {e}")
        
        # Handler padrão de erro
        error_messages = {
            404: "Not Found",
            500: "Internal Server Error",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden"
        }
        
        res.status(status_code).json({
            "error": error_messages.get(status_code, "Error"),
            "message": message or error_messages.get(status_code, "Error"),
            "status": status_code
        })
    
    def _create_request_handler(self):
        """Cria o handler de requisições HTTP"""
        
        class RequestHandler(BaseHTTPRequestHandler):
            def __init__(self, *args, framework=None, **kwargs):
                self.framework = framework
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                self._handle_request('GET')
            
            def do_POST(self):
                self._handle_request('POST')
            
            def do_PUT(self):
                self._handle_request('PUT')
            
            def do_DELETE(self):
                self._handle_request('DELETE')
            
            def do_PATCH(self):
                self._handle_request('PATCH')
            
            def do_OPTIONS(self):
                self._handle_request('OPTIONS')
            
            def _handle_request(self, method):
                try:
                    # Lê o corpo da requisição
                    content_length = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
                    
                    # Cria objetos Request e Response
                    req = Request(method, self.path, dict(self.headers), body)
                    res = Response()
                    
                    # Executa middlewares
                    if not self.framework._execute_middlewares(req, res):
                        if not res._sent:
                            res.status(403).json({"error": "Forbidden", "message": "Access denied by middleware"})
                    else:
                        # Encontra a rota
                        route = self.framework._find_route(method, self.path)
                        
                        if route:
                            # Extrai parâmetros da URL
                            req.params = route.extract_params(self.path)
                            
                            # Executa o handler da rota
                            try:
                                route.handler(req, res)
                            except Exception as e:
                                print(f"Erro no handler da rota: {e}")
                                if not res._sent:
                                    self.framework._handle_error(500, req, res, str(e))
                        else:
                            # Rota não encontrada
                            self.framework._handle_error(404, req, res)
                    
                    # Envia a resposta
                    if not res._sent:
                        res.json({"error": "No response sent"})
                    
                    self.send_response(res.status_code)
                    for key, value in res.headers.items():
                        self.send_header(key, value)
                    self.end_headers()
                    self.wfile.write(res.body.encode('utf-8'))
                
                except Exception as e:
                    print(f"Erro geral na requisição: {e}")
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    error_response = json.dumps({"error": "Internal Server Error", "message": str(e)})
                    self.wfile.write(error_response.encode('utf-8'))
            
            def log_message(self, format, *args):
                """Override para personalizar logs"""
                print(f"[{self.log_date_time_string()}] {format % args}")
        
        return RequestHandler
    
    def listen(self, port: int = 3000, host: str = 'localhost', debug: bool = False):
        """Inicia o servidor"""
        def handler(*args, **kwargs):
            RequestHandler = self._create_request_handler()
            return RequestHandler(*args, framework=self, **kwargs)
        
        server = HTTPServer((host, port), handler)
        
        if debug:
            print(f"""
╔══════════════════════════════════════╗
║         PYREST-FRAMEWORK             ║
║    Framework Python para APIs REST   ║
╠══════════════════════════════════════╣
║  🚀 Servidor rodando em:             ║
║     http://{host}:{port}{'':>{35-len(host)-len(str(port))}}║
║                                      ║
║  📚 Desenvolvido para ADS            ║
║  ⚡ Pressione Ctrl+C para parar      ║
╚══════════════════════════════════════╝
            """)
        else:
            print(f"🚀 PyRest servidor rodando em http://{host}:{port}")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Servidor parado pelo usuário")
            server.shutdown()
    
    def run(self, **kwargs):
        """Alias para listen() - compatibilidade com Flask"""
        self.listen(**kwargs)