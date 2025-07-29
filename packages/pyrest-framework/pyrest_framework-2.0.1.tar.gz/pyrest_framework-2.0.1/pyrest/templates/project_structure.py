"""
Template de Estrutura de Projeto PYREST-FRAMEWORK
Estrutura completa com Controllers, Services e Models
"""

PROJECT_STRUCTURE = {
    "app.py": '''"""
Aplicação Principal - {project_name}
"""

from pyrest import create_app, Middlewares
from controllers.user_controller import UserController
from controllers.product_controller import ProductController
from services.user_service import UserService
from services.product_service import ProductService
from models.user import User
from models.product import Product
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository

# Cria a aplicação
app = create_app()

# Middlewares
app.use(Middlewares.cors())
app.use(Middlewares.logger('dev'))
app.use(Middlewares.json_parser())

# Repositórios
user_repository = UserRepository()
product_repository = ProductRepository()

# Services
user_service = UserService(user_repository)
product_service = ProductService(product_repository)

# Controllers
user_controller = UserController(user_service)
product_controller = ProductController(product_service)

# Importa as rotas
from routes.user_routes import setup_user_routes
from routes.product_routes import setup_product_routes

# Configura as rotas
setup_user_routes(app, user_controller)
setup_product_routes(app, product_controller)

# Rota principal
@app.get('/')
def home(req, res):
    res.json({{
        "message": "API {project_name}",
        "version": "1.0.0",
        "framework": "PYREST-FRAMEWORK"
    }})

if __name__ == '__main__':
    app.listen(port=3000, debug=True)
''',

    "controllers/__init__.py": '''"""
Controllers Package
"""''',

    "controllers/user_controller.py": '''"""
User Controller
"""

from pyrest import Controller

class UserController(Controller):
    def __init__(self, user_service):
        super().__init__(user_service)
    
    def login(self):
        """Método de login"""
        data = self.request.get_json()
        return self.service.login(data)
    
    def register(self):
        """Método de registro"""
        data = self.request.get_json()
        return self.service.register(data)
''',

    "controllers/product_controller.py": '''"""
Product Controller
"""

from pyrest import Controller

class ProductController(Controller):
    def __init__(self, product_service):
        super().__init__(product_service)
    
    def search(self):
        """Busca produtos"""
        query = self.request.get_query('q', '')
        return self.service.search(query)
''',

    "services/__init__.py": '''"""
Services Package
"""''',

    "services/user_service.py": '''"""
User Service
"""

from pyrest import Service

class UserService(Service):
    def __init__(self, user_repository):
        super().__init__(user_repository)
    
    def login(self, credentials):
        """Autentica um usuário"""
        email = credentials.get('email')
        password = credentials.get('password')
        
        user = self.repository.find_by_email(email)
        if user and self._verify_password(password, user.get('password', '')):
            return {{
                'user': user,
                'token': self._generate_token(user)
            }}
        return None
    
    def register(self, user_data):
        """Registra um novo usuário"""
        if 'password' in user_data:
            user_data['password'] = self._hash_password(user_data['password'])
        return self.repository.create(user_data)
    
    def _hash_password(self, password):
        """Hash da password"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password, hashed):
        """Verifica a password"""
        return self._hash_password(password) == hashed
    
    def _generate_token(self, user):
        """Gera token JWT"""
        import time
        import hashlib
        return hashlib.sha256(f"{{user.get('id')}}{{time.time()}}".encode()).hexdigest()
''',

    "services/product_service.py": '''"""
Product Service
"""

from pyrest import Service

class ProductService(Service):
    def __init__(self, product_repository):
        super().__init__(product_repository)
    
    def search(self, query):
        """Busca produtos por query"""
        return self.repository.search(query)
    
    def get_by_category(self, category):
        """Retorna produtos por categoria"""
        return self.repository.find_by_category(category)
''',

    "models/__init__.py": '''"""
Models Package
"""''',

    "models/user.py": '''"""
User Model
"""

from pyrest import Model

class User(Model):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.email = kwargs.get('email', '')
        self.password = kwargs.get('password', '')
        self.role = kwargs.get('role', 'user')
        self.is_active = kwargs.get('is_active', True)
        super().__init__(**kwargs)
    
    def to_dict(self):
        """Converte para dicionário (exclui password)"""
        data = super().to_dict()
        data.pop('password', None)
        return data
''',

    "models/product.py": '''"""
Product Model
"""

from pyrest import Model

class Product(Model):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.price = kwargs.get('price', 0.0)
        self.stock = kwargs.get('stock', 0)
        self.category = kwargs.get('category', '')
        self.image_url = kwargs.get('image_url', '')
        super().__init__(**kwargs)
''',

    "repositories/__init__.py": '''"""
Repositories Package
"""''',

    "repositories/user_repository.py": '''"""
User Repository
"""

from pyrest import InMemoryRepository

class UserRepository(InMemoryRepository):
    def find_by_email(self, email):
        """Encontra usuário por email"""
        for user in self.data.values():
            if user.get('email') == email:
                return user
        return None
''',

    "repositories/product_repository.py": '''"""
Product Repository
"""

from pyrest import InMemoryRepository

class ProductRepository(InMemoryRepository):
    def search(self, query):
        """Busca produtos por query"""
        results = []
        query_lower = query.lower()
        
        for product in self.data.values():
            if (query_lower in product.get('name', '').lower() or
                query_lower in product.get('description', '').lower()):
                results.append(product)
        
        return results
    
    def find_by_category(self, category):
        """Encontra produtos por categoria"""
        results = []
        category_lower = category.lower()
        
        for product in self.data.values():
            if category_lower in product.get('category', '').lower():
                results.append(product)
        
        return results
''',

    "routes/__init__.py": '''"""
Routes Package
"""''',

    "routes/user_routes.py": '''"""
User Routes
"""

from pyrest import validate_user, ValidationError

def setup_user_routes(app, user_controller):
    @app.get('/users')
    def get_users(req, res):
        """Lista todos os usuários"""
        user_controller.set_context(req, res)
        result = user_controller.index()
        res.json(result)
    
    @app.get('/users/:id')
    def get_user(req, res):
        """Obtém um usuário específico"""
        user_controller.set_context(req, res)
        user_id = req.params['id']
        result = user_controller.show(user_id)
        
        if result:
            res.json(result)
        else:
            res.status(404).json({{"error": "Usuário não encontrado"}})
    
    @app.post('/users')
    def create_user(req, res):
        """Cria um novo usuário"""
        try:
            validated_data = validate_user(req.get_json())
            user_controller.set_context(req, res)
            result = user_controller.store(validated_data)
            res.status(201).json(result)
        except ValidationError as e:
            res.status(400).json({{
                "error": "Dados inválidos",
                "details": e.field
            }})
    
    @app.put('/users/:id')
    def update_user(req, res):
        """Atualiza um usuário"""
        try:
            user_id = req.params['id']
            validated_data = validate_user(req.get_json())
            user_controller.set_context(req, res)
            result = user_controller.update(user_id, validated_data)
            
            if result:
                res.json(result)
            else:
                res.status(404).json({{"error": "Usuário não encontrado"}})
        except ValidationError as e:
            res.status(400).json({{
                "error": "Dados inválidos",
                "details": e.field
            }})
    
    @app.delete('/users/:id')
    def delete_user(req, res):
        """Remove um usuário"""
        user_controller.set_context(req, res)
        user_id = req.params['id']
        result = user_controller.destroy(user_id)
        
        if result:
            res.json({{"message": "Usuário removido com sucesso"}})
        else:
            res.status(404).json({{"error": "Usuário não encontrado"}})
    
    @app.post('/login')
    def login(req, res):
        """Login de usuário"""
        user_controller.set_context(req, res)
        result = user_controller.login()
        
        if result:
            res.json(result)
        else:
            res.status(401).json({{"error": "Credenciais inválidas"}})
    
    @app.post('/register')
    def register(req, res):
        """Registro de usuário"""
        try:
            validated_data = validate_user(req.get_json())
            user_controller.set_context(req, res)
            result = user_controller.register()
            res.status(201).json(result)
        except ValidationError as e:
            res.status(400).json({{
                "error": "Dados inválidos",
                "details": e.field
            }})
''',

    "routes/product_routes.py": '''"""
Product Routes
"""

from pyrest import validate_product, ValidationError

def setup_product_routes(app, product_controller):
    @app.get('/products')
    def get_products(req, res):
        """Lista todos os produtos"""
        product_controller.set_context(req, res)
        result = product_controller.index()
        res.json(result)
    
    @app.get('/products/:id')
    def get_product(req, res):
        """Obtém um produto específico"""
        product_controller.set_context(req, res)
        product_id = req.params['id']
        result = product_controller.show(product_id)
        
        if result:
            res.json(result)
        else:
            res.status(404).json({{"error": "Produto não encontrado"}})
    
    @app.post('/products')
    def create_product(req, res):
        """Cria um novo produto"""
        try:
            validated_data = validate_product(req.get_json())
            product_controller.set_context(req, res)
            result = product_controller.store(validated_data)
            res.status(201).json(result)
        except ValidationError as e:
            res.status(400).json({{
                "error": "Dados inválidos",
                "details": e.field
            }})
    
    @app.put('/products/:id')
    def update_product(req, res):
        """Atualiza um produto"""
        try:
            product_id = req.params['id']
            validated_data = validate_product(req.get_json())
            product_controller.set_context(req, res)
            result = product_controller.update(product_id, validated_data)
            
            if result:
                res.json(result)
            else:
                res.status(404).json({{"error": "Produto não encontrado"}})
        except ValidationError as e:
            res.status(400).json({{
                "error": "Dados inválidos",
                "details": e.field
            }})
    
    @app.delete('/products/:id')
    def delete_product(req, res):
        """Remove um produto"""
        product_controller.set_context(req, res)
        product_id = req.params['id']
        result = product_controller.destroy(product_id)
        
        if result:
            res.json({{"message": "Produto removido com sucesso"}})
        else:
            res.status(404).json({{"error": "Produto não encontrado"}})
    
    @app.get('/products/search')
    def search_products(req, res):
        """Busca produtos"""
        product_controller.set_context(req, res)
        result = product_controller.search()
        res.json(result)
''',

    "middlewares/__init__.py": '''"""
Custom Middlewares Package
"""''',

    "middlewares/auth_middleware.py": '''"""
Authentication Middleware
"""

def auth_middleware(req, res):
    """Middleware de autenticação"""
    # Rotas públicas
    public_routes = ['/login', '/register', '/']
    
    if req.path in public_routes:
        return True
    
    # Verifica token
    auth_header = req.get_header('authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        res.status(401).json({{
            "error": "Token required"
        }})
        return False
    
    token = auth_header[7:]
    
    # Aqui você implementaria a verificação real do token
    # Por enquanto, aceita qualquer token
    return True
''',

    "utils/__init__.py": '''"""
Utils Package
"""''',

    "utils/helpers.py": '''"""
Helper Functions
"""

import hashlib
import time

def generate_id():
    """Gera um ID único"""
    return hashlib.sha256(f"{{time.time()}}".encode()).hexdigest()[:8]

def format_price(price):
    """Formata preço"""
    return f"R$ {{price:.2f}}"

def slugify(text):
    """Converte texto para slug"""
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9\\s-]', '', text)
    text = re.sub(r'\\s+', '-', text)
    return text.strip('-')
''',

    "tests/__init__.py": '''"""
Tests Package
"""''',

    "tests/test_users.py": '''"""
User Tests
"""

import unittest
from unittest.mock import Mock
from pyrest import create_app, UserController, UserService, InMemoryRepository

class TestUsers(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.repository = InMemoryRepository()
        self.service = UserService(self.repository)
        self.controller = UserController(self.service)
    
    def test_create_user(self):
        """Testa criação de usuário"""
        user_data = {{
            "name": "Test User",
            "email": "test@example.com",
            "password": "123456"
        }}
        
        result = self.repository.create(user_data)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "Test User")
        self.assertEqual(result['email'], "test@example.com")
    
    def test_find_user_by_email(self):
        """Testa busca de usuário por email"""
        user_data = {{
            "name": "Test User",
            "email": "test@example.com",
            "password": "123456"
        }}
        
        self.repository.create(user_data)
        user = self.repository.find_by_email("test@example.com")
        
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], "test@example.com")

if __name__ == '__main__':
    unittest.main()
''',

    "tests/test_products.py": '''"""
Product Tests
"""

import unittest
from pyrest import ProductController, ProductService, InMemoryRepository

class TestProducts(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryRepository()
        self.service = ProductService(self.repository)
        self.controller = ProductController(self.service)
    
    def test_create_product(self):
        """Testa criação de produto"""
        product_data = {{
            "name": "Test Product",
            "description": "Test Description",
            "price": 100.00,
            "stock": 10
        }}
        
        result = self.repository.create(product_data)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "Test Product")
        self.assertEqual(result['price'], 100.00)
    
    def test_search_products(self):
        """Testa busca de produtos"""
        product_data = {{
            "name": "Laptop Gaming",
            "description": "High performance laptop",
            "price": 2000.00,
            "stock": 5
        }}
        
        self.repository.create(product_data)
        results = self.repository.search("laptop")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Laptop Gaming")

if __name__ == '__main__':
    unittest.main()
''',

    "config/__init__.py": '''"""
Configuration Package
"""''',

    "config/database.py": '''"""
Database Configuration
"""

# Configurações de banco de dados
DATABASE_CONFIG = {{
    "host": "localhost",
    "port": 5432,
    "database": "myapp",
    "username": "postgres",
    "password": "password"
}}

# Configurações do Prisma
PRISMA_CONFIG = {{
    "schema_path": "prisma/schema.prisma",
    "database_url": "postgresql://postgres:password@localhost:5432/myapp"
}}
''',

    "config/app.py": '''"""
Application Configuration
"""

# Configurações da aplicação
APP_CONFIG = {{
    "debug": True,
    "host": "localhost",
    "port": 3000,
    "secret_key": "your-secret-key-here"
}}

# Configurações de CORS
CORS_CONFIG = {{
    "origin": "*",
    "credentials": True
}}
''',

    "README.md": '''# {project_name}

API desenvolvida com PYREST-FRAMEWORK

## Estrutura do Projeto

```
{project_name}/
├── app.py                 # Aplicação principal
├── controllers/           # Controllers
├── services/             # Services
├── models/               # Models
├── repositories/         # Repositórios
├── routes/               # Rotas
├── middlewares/          # Middlewares customizados
├── utils/                # Utilitários
├── tests/                # Testes
├── config/               # Configurações
└── README.md             # Este arquivo
```

## Instalação

```bash
pip install pyrest-framework
```

## Execução

```bash
python app.py
```

## Endpoints

### Usuários
- `GET /users` - Lista usuários
- `POST /users` - Cria usuário
- `GET /users/:id` - Obtém usuário
- `PUT /users/:id` - Atualiza usuário
- `DELETE /users/:id` - Remove usuário
- `POST /login` - Login
- `POST /register` - Registro

### Produtos
- `GET /products` - Lista produtos
- `POST /products` - Cria produto
- `GET /products/:id` - Obtém produto
- `PUT /products/:id` - Atualiza produto
- `DELETE /products/:id` - Remove produto
- `GET /products/search?q=termo` - Busca produtos

## Desenvolvimento

### Executar Testes
```bash
python -m pytest tests/
```

### Estrutura MVC
- **Controllers**: Lógica de negócio
- **Services**: Camada de serviços
- **Models**: Modelos de dados
- **Repositories**: Acesso a dados
- **Routes**: Definição de rotas
- **Middlewares**: Interceptadores
''',

    "requirements.txt": '''pyrest-framework>=2.0.0
pytest>=6.0.0
requests>=2.25.0
''',

    ".gitignore": '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite3

# Environment variables
.env
.env.local
'''
} 