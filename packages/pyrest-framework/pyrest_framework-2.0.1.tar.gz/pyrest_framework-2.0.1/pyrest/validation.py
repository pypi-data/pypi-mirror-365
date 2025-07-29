"""
Sistema de Validação para PYREST-FRAMEWORK
Validação de dados de entrada
"""

from typing import Any, Dict, List, Optional, Union
import re
from datetime import datetime

class ValidationError(Exception):
    """Exceção para erros de validação"""
    
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class Validator:
    """Classe base para validadores"""
    
    def __init__(self, field_name: str):
        self.field_name = field_name
        self.value = None
        self.errors = []
    
    def validate(self, value: Any) -> bool:
        """Valida um valor"""
        self.value = value
        self.errors = []
        return True
    
    def add_error(self, message: str):
        """Adiciona um erro"""
        self.errors.append(message)
    
    def get_errors(self) -> List[str]:
        """Retorna os erros"""
        return self.errors

class RequiredValidator(Validator):
    """Validador para campos obrigatórios"""
    
    def validate(self, value: Any) -> bool:
        super().validate(value)
        
        if value is None or (isinstance(value, str) and not value.strip()):
            self.add_error(f"O campo '{self.field_name}' é obrigatório")
            return False
        
        return True

class StringValidator(Validator):
    """Validador para strings"""
    
    def __init__(self, field_name: str, min_length: int = None, max_length: int = None):
        super().__init__(field_name)
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, value: Any) -> bool:
        super().validate(value)
        
        if value is not None and not isinstance(value, str):
            self.add_error(f"O campo '{self.field_name}' deve ser uma string")
            return False
        
        if value is not None:
            if self.min_length and len(value) < self.min_length:
                self.add_error(f"O campo '{self.field_name}' deve ter pelo menos {self.min_length} caracteres")
                return False
            
            if self.max_length and len(value) > self.max_length:
                self.add_error(f"O campo '{self.field_name}' deve ter no máximo {self.max_length} caracteres")
                return False
        
        return True

class EmailValidator(Validator):
    """Validador para emails"""
    
    def validate(self, value: Any) -> bool:
        super().validate(value)
        
        if value is not None:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(value)):
                self.add_error(f"O campo '{self.field_name}' deve ser um email válido")
                return False
        
        return True

class NumberValidator(Validator):
    """Validador para números"""
    
    def __init__(self, field_name: str, min_value: float = None, max_value: float = None):
        super().__init__(field_name)
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any) -> bool:
        super().validate(value)
        
        if value is not None:
            try:
                num_value = float(value)
                if self.min_value is not None and num_value < self.min_value:
                    self.add_error(f"O campo '{self.field_name}' deve ser maior ou igual a {self.min_value}")
                    return False
                
                if self.max_value is not None and num_value > self.max_value:
                    self.add_error(f"O campo '{self.field_name}' deve ser menor ou igual a {self.max_value}")
                    return False
            except (ValueError, TypeError):
                self.add_error(f"O campo '{self.field_name}' deve ser um número válido")
                return False
        
        return True

class IntegerValidator(NumberValidator):
    """Validador para números inteiros"""
    
    def validate(self, value: Any) -> bool:
        super().validate(value)
        
        if value is not None:
            try:
                int(value)
            except (ValueError, TypeError):
                self.add_error(f"O campo '{self.field_name}' deve ser um número inteiro")
                return False
        
        return True

class BooleanValidator(Validator):
    """Validador para booleanos"""
    
    def validate(self, value: Any) -> bool:
        super().validate(value)
        
        if value is not None and not isinstance(value, bool):
            self.add_error(f"O campo '{self.field_name}' deve ser um booleano")
            return False
        
        return True

class DateValidator(Validator):
    """Validador para datas"""
    
    def __init__(self, field_name: str, format: str = "%Y-%m-%d"):
        super().__init__(field_name)
        self.format = format
    
    def validate(self, value: Any) -> bool:
        super().validate(value)
        
        if value is not None:
            if isinstance(value, str):
                try:
                    datetime.strptime(value, self.format)
                except ValueError:
                    self.add_error(f"O campo '{self.field_name}' deve ser uma data válida no formato {self.format}")
                    return False
            elif not isinstance(value, datetime):
                self.add_error(f"O campo '{self.field_name}' deve ser uma data válida")
                return False
        
        return True

class ArrayValidator(Validator):
    """Validador para arrays"""
    
    def __init__(self, field_name: str, min_items: int = None, max_items: int = None):
        super().__init__(field_name)
        self.min_items = min_items
        self.max_items = max_items
    
    def validate(self, value: Any) -> bool:
        super().validate(value)
        
        if value is not None:
            if not isinstance(value, (list, tuple)):
                self.add_error(f"O campo '{self.field_name}' deve ser uma lista")
                return False
            
            if self.min_items is not None and len(value) < self.min_items:
                self.add_error(f"O campo '{self.field_name}' deve ter pelo menos {self.min_items} itens")
                return False
            
            if self.max_items is not None and len(value) > self.max_items:
                self.add_error(f"O campo '{self.field_name}' deve ter no máximo {self.max_items} itens")
                return False
        
        return True

class ValidationSchema:
    """Schema de validação"""
    
    def __init__(self):
        self.validators = {}
    
    def add_validator(self, field: str, validator: Validator):
        """Adiciona um validador para um campo"""
        if field not in self.validators:
            self.validators[field] = []
        self.validators[field].append(validator)
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida os dados"""
        errors = {}
        validated_data = {}
        
        for field, validators in self.validators.items():
            value = data.get(field)
            
            for validator in validators:
                if not validator.validate(value):
                    if field not in errors:
                        errors[field] = []
                    errors[field].extend(validator.get_errors())
            
            if field not in errors:
                validated_data[field] = value
        
        if errors:
            raise ValidationError("Dados inválidos", errors)
        
        return validated_data

# Funções utilitárias para validação rápida
def validate_required(data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Valida campos obrigatórios"""
    schema = ValidationSchema()
    
    for field in fields:
        schema.add_validator(field, RequiredValidator(field))
    
    return schema.validate(data)

def validate_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida dados de usuário"""
    schema = ValidationSchema()
    
    schema.add_validator('name', RequiredValidator('name'))
    schema.add_validator('name', StringValidator('name', min_length=2, max_length=100))
    
    schema.add_validator('email', RequiredValidator('email'))
    schema.add_validator('email', EmailValidator('email'))
    
    schema.add_validator('password', RequiredValidator('password'))
    schema.add_validator('password', StringValidator('password', min_length=6))
    
    return schema.validate(data)

def validate_product(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida dados de produto"""
    schema = ValidationSchema()
    
    schema.add_validator('name', RequiredValidator('name'))
    schema.add_validator('name', StringValidator('name', min_length=2, max_length=200))
    
    schema.add_validator('price', NumberValidator('price', min_value=0))
    
    schema.add_validator('stock', IntegerValidator('stock', min_value=0))
    
    return schema.validate(data) 