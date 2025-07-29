"""
Controllers para PYREST-FRAMEWORK
Sistema de controllers para organizar a lógica de negócio
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from .request import Request
from .response import Response

class BaseController(ABC):
    """Classe base para todos os controllers"""
    
    def __init__(self):
        self.request: Optional[Request] = None
        self.response: Optional[Response] = None
    
    def set_context(self, request: Request, response: Response):
        """Define o contexto da requisição"""
        self.request = request
        self.response = response
    
    @abstractmethod
    def index(self) -> Dict[str, Any]:
        """Lista todos os recursos"""
        pass
    
    @abstractmethod
    def show(self, id: str) -> Dict[str, Any]:
        """Mostra um recurso específico"""
        pass
    
    @abstractmethod
    def store(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo recurso"""
        pass
    
    @abstractmethod
    def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza um recurso"""
        pass
    
    @abstractmethod
    def destroy(self, id: str) -> Dict[str, Any]:
        """Remove um recurso"""
        pass

class Controller(BaseController):
    """Controller genérico com implementações padrão"""
    
    def __init__(self, service=None):
        super().__init__()
        self.service = service
    
    def index(self) -> Dict[str, Any]:
        """Lista todos os recursos"""
        if self.service:
            return self.service.get_all()
        return {"message": "Index method not implemented"}
    
    def show(self, id: str) -> Dict[str, Any]:
        """Mostra um recurso específico"""
        if self.service:
            return self.service.get_by_id(id)
        return {"message": "Show method not implemented"}
    
    def store(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo recurso"""
        if self.service:
            return self.service.create(data)
        return {"message": "Store method not implemented"}
    
    def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza um recurso"""
        if self.service:
            return self.service.update(id, data)
        return {"message": "Update method not implemented"}
    
    def destroy(self, id: str) -> Dict[str, Any]:
        """Remove um recurso"""
        if self.service:
            return self.service.delete(id)
        return {"message": "Destroy method not implemented"}

class UserController(Controller):
    """Controller específico para usuários"""
    
    def __init__(self, user_service=None):
        super().__init__(user_service)
    
    def login(self) -> Dict[str, Any]:
        """Método de login"""
        data = self.request.get_json()
        if self.service:
            return self.service.login(data)
        return {"message": "Login method not implemented"}
    
    def register(self) -> Dict[str, Any]:
        """Método de registro"""
        data = self.request.get_json()
        if self.service:
            return self.service.register(data)
        return {"message": "Register method not implemented"}

class ProductController(Controller):
    """Controller específico para produtos"""
    
    def __init__(self, product_service=None):
        super().__init__(product_service)
    
    def search(self) -> Dict[str, Any]:
        """Busca produtos"""
        query = self.request.get_query('q', '')
        if self.service:
            return self.service.search(query)
        return {"message": "Search method not implemented"}

# Decorator para facilitar o uso de controllers
def controller_method(method_name: str):
    """Decorator para métodos de controller"""
    def decorator(func):
        def wrapper(controller_instance, *args, **kwargs):
            if controller_instance.request and controller_instance.response:
                result = func(controller_instance, *args, **kwargs)
                controller_instance.response.json(result)
                return result
            return func(controller_instance, *args, **kwargs)
        return wrapper
    return decorator 