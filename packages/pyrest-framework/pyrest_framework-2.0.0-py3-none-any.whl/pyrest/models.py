"""
Models para PYREST-FRAMEWORK
Sistema de models com suporte a Prisma e outros ORMs
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar
from datetime import datetime
import json

T = TypeVar('T', bound='BaseModel')

class BaseModel(ABC):
    """Classe base para todos os models"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())
        
        # Define os campos do model
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Converte o model para dicionário"""
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> 'BaseModel':
        """Cria um model a partir de um dicionário"""
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

class Model(BaseModel):
    """Model genérico com implementações padrão"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o model para dicionário"""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            else:
                data[key] = value
        return data
    
    def from_dict(self, data: Dict[str, Any]) -> 'Model':
        """Cria um model a partir de um dicionário"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

class User(Model):
    """Model para usuários"""
    
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.email = kwargs.get('email', '')
        self.password = kwargs.get('password', '')
        self.role = kwargs.get('role', 'user')
        self.is_active = kwargs.get('is_active', True)
        super().__init__(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário (exclui password)"""
        data = super().to_dict()
        data.pop('password', None)  # Não retorna a password
        return data

class Product(Model):
    """Model para produtos"""
    
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.price = kwargs.get('price', 0.0)
        self.stock = kwargs.get('stock', 0)
        self.category = kwargs.get('category', '')
        self.image_url = kwargs.get('image_url', '')
        super().__init__(**kwargs)

# Sistema de Prisma Integration
class PrismaManager:
    """Gerenciador de conexão com Prisma"""
    
    def __init__(self, schema_path: str = "prisma/schema.prisma"):
        self.schema_path = schema_path
        self.client = None
        self._init_prisma()
    
    def _init_prisma(self):
        """Inicializa o cliente Prisma"""
        try:
            from prisma import Prisma
            self.client = Prisma()
        except ImportError:
            print("⚠️ Prisma não instalado. Execute: pip install prisma")
            self.client = None
    
    def connect(self):
        """Conecta ao banco de dados"""
        if self.client:
            self.client.connect()
    
    def disconnect(self):
        """Desconecta do banco de dados"""
        if self.client:
            self.client.disconnect()
    
    def generate_client(self):
        """Gera o cliente Prisma"""
        if self.client:
            self.client.generate()

class PrismaRepository:
    """Repositório baseado em Prisma"""
    
    def __init__(self, model_name: str, prisma_manager: PrismaManager):
        self.model_name = model_name
        self.prisma = prisma_manager
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Encontra todos os registros"""
        if not self.prisma.client:
            return []
        
        try:
            result = getattr(self.prisma.client, self.model_name.lower()).find_many()
            return [item.dict() for item in result]
        except Exception as e:
            print(f"Erro ao buscar {self.model_name}: {e}")
            return []
    
    def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Encontra por ID"""
        if not self.prisma.client:
            return None
        
        try:
            result = getattr(self.prisma.client, self.model_name.lower()).find_unique(
                where={'id': id}
            )
            return result.dict() if result else None
        except Exception as e:
            print(f"Erro ao buscar {self.model_name} por ID: {e}")
            return None
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo registro"""
        if not self.prisma.client:
            return data
        
        try:
            result = getattr(self.prisma.client, self.model_name.lower()).create(
                data=data
            )
            return result.dict()
        except Exception as e:
            print(f"Erro ao criar {self.model_name}: {e}")
            return data
    
    def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um registro"""
        if not self.prisma.client:
            return None
        
        try:
            result = getattr(self.prisma.client, self.model_name.lower()).update(
                where={'id': id},
                data=data
            )
            return result.dict()
        except Exception as e:
            print(f"Erro ao atualizar {self.model_name}: {e}")
            return None
    
    def delete(self, id: str) -> bool:
        """Remove um registro"""
        if not self.prisma.client:
            return False
        
        try:
            getattr(self.prisma.client, self.model_name.lower()).delete(
                where={'id': id}
            )
            return True
        except Exception as e:
            print(f"Erro ao remover {self.model_name}: {e}")
            return False

# Repositório em memória para desenvolvimento
class InMemoryRepository:
    """Repositório em memória para desenvolvimento"""
    
    def __init__(self):
        self.data = {}
        self.counter = 1
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Retorna todos os registros"""
        return list(self.data.values())
    
    def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Encontra por ID"""
        return self.data.get(str(id))
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo registro"""
        data['id'] = str(self.counter)
        data['created_at'] = datetime.now().isoformat()
        data['updated_at'] = datetime.now().isoformat()
        self.data[str(self.counter)] = data
        self.counter += 1
        return data
    
    def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um registro"""
        if str(id) in self.data:
            self.data[str(id)].update(data)
            self.data[str(id)]['updated_at'] = datetime.now().isoformat()
            return self.data[str(id)]
        return None
    
    def delete(self, id: str) -> bool:
        """Remove um registro"""
        if str(id) in self.data:
            del self.data[str(id)]
            return True
        return False 