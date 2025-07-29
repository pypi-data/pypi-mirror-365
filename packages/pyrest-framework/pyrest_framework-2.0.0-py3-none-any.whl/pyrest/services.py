"""
Services para PYREST-FRAMEWORK
Sistema de services para a camada de lógica de negócio
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from .models import BaseModel

class BaseService(ABC):
    """Classe base para todos os services"""
    
    def __init__(self, repository=None):
        self.repository = repository
    
    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todos os registros"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retorna um registro por ID"""
        pass
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo registro"""
        pass
    
    @abstractmethod
    def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um registro"""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Remove um registro"""
        pass

class Service(BaseService):
    """Service genérico com implementações padrão"""
    
    def __init__(self, repository=None, model_class=None):
        super().__init__(repository)
        self.model_class = model_class
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todos os registros"""
        if self.repository:
            return self.repository.find_all()
        return []
    
    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retorna um registro por ID"""
        if self.repository:
            return self.repository.find_by_id(id)
        return None
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo registro"""
        if self.repository:
            return self.repository.create(data)
        return data
    
    def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um registro"""
        if self.repository:
            return self.repository.update(id, data)
        return None
    
    def delete(self, id: str) -> bool:
        """Remove um registro"""
        if self.repository:
            return self.repository.delete(id)
        return False

class UserService(Service):
    """Service específico para usuários"""
    
    def __init__(self, user_repository=None):
        super().__init__(user_repository)
    
    def login(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Autentica um usuário"""
        email = credentials.get('email')
        password = credentials.get('password')
        
        if self.repository:
            user = self.repository.find_by_email(email)
            if user and self._verify_password(password, user.get('password', '')):
                return {
                    'user': user,
                    'token': self._generate_token(user)
                }
        return None
    
    def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registra um novo usuário"""
        # Hash da password
        if 'password' in user_data:
            user_data['password'] = self._hash_password(user_data['password'])
        
        if self.repository:
            return self.repository.create(user_data)
        return user_data
    
    def _hash_password(self, password: str) -> str:
        """Hash da password (implementação básica)"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verifica a password"""
        return self._hash_password(password) == hashed
    
    def _generate_token(self, user: Dict[str, Any]) -> str:
        """Gera token JWT (implementação básica)"""
        import time
        import hashlib
        return hashlib.sha256(f"{user.get('id')}{time.time()}".encode()).hexdigest()

class ProductService(Service):
    """Service específico para produtos"""
    
    def __init__(self, product_repository=None):
        super().__init__(product_repository)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Busca produtos por query"""
        if self.repository:
            return self.repository.search(query)
        return []
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Retorna produtos por categoria"""
        if self.repository:
            return self.repository.find_by_category(category)
        return []
    
    def update_stock(self, id: str, quantity: int) -> bool:
        """Atualiza o stock de um produto"""
        if self.repository:
            product = self.repository.find_by_id(id)
            if product:
                new_stock = product.get('stock', 0) + quantity
                return self.repository.update(id, {'stock': new_stock})
        return False 