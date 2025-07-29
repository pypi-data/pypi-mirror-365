"""
Exemplo com Prisma e PostgreSQL - PYREST-FRAMEWORK
Demonstra a integração completa com banco de dados
"""

import os
from pyrest import (
    create_app, Middlewares,
    UserController, UserService, User,
    ProductController, ProductService, Product,
    PrismaRepository, validate_user, validate_product,
    ValidationError, setup_database, DatabaseConfig
)

# Configuração do banco de dados
# Você pode usar variáveis de ambiente ou definir diretamente
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/pyrest_demo')

# Cria a aplicação
app = create_app()

# Middlewares
app.use(Middlewares.cors())
app.use(Middlewares.logger('dev'))
app.use(Middlewares.json_parser())

# Inicializa o banco de dados
print("🚀 Configurando banco de dados...")
db_manager = setup_database(DATABASE_URL, "postgresql", auto_setup=True)

if db_manager.client:
    # Repositórios com Prisma
    user_repository = PrismaRepository("user", db_manager)
    product_repository = PrismaRepository("product", db_manager)
    
    # Services
    user_service = UserService(user_repository)
    product_service = ProductService(product_repository)
    
    # Controllers
    user_controller = UserController(user_service)
    product_controller = ProductController(product_service)
    
    print("✅ Banco de dados configurado com sucesso!")
else:
    print("⚠️ Usando repositório em memória (Prisma não disponível)")
    from pyrest import InMemoryRepository
    
    # Fallback para repositório em memória
    user_repository = InMemoryRepository()
    product_repository = InMemoryRepository()
    
    # Services
    user_service = UserService(user_repository)
    product_service = ProductService(product_repository)
    
    # Controllers
    user_controller = UserController(user_service)
    product_controller = ProductController(product_service)

# Rotas de Usuários
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
        res.status(404).json({"error": "Usuário não encontrado"})

@app.post('/users')
def create_user(req, res):
    """Cria um novo usuário"""
    try:
        validated_data = validate_user(req.get_json())
        user_controller.set_context(req, res)
        result = user_controller.store(validated_data)
        res.status(201).json(result)
    except ValidationError as e:
        res.status(400).json({
            "error": "Dados inválidos",
            "details": e.field
        })

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
            res.status(404).json({"error": "Usuário não encontrado"})
    except ValidationError as e:
        res.status(400).json({
            "error": "Dados inválidos",
            "details": e.field
        })

@app.delete('/users/:id')
def delete_user(req, res):
    """Remove um usuário"""
    user_controller.set_context(req, res)
    user_id = req.params['id']
    result = user_controller.destroy(user_id)
    
    if result:
        res.json({"message": "Usuário removido com sucesso"})
    else:
        res.status(404).json({"error": "Usuário não encontrado"})

@app.post('/login')
def login(req, res):
    """Login de usuário"""
    user_controller.set_context(req, res)
    result = user_controller.login()
    
    if result:
        res.json(result)
    else:
        res.status(401).json({"error": "Credenciais inválidas"})

@app.post('/register')
def register(req, res):
    """Registro de usuário"""
    try:
        validated_data = validate_user(req.get_json())
        user_controller.set_context(req, res)
        result = user_controller.register()
        res.status(201).json(result)
    except ValidationError as e:
        res.status(400).json({
            "error": "Dados inválidos",
            "details": e.field
        })

# Rotas de Produtos
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
        res.status(404).json({"error": "Produto não encontrado"})

@app.post('/products')
def create_product(req, res):
    """Cria um novo produto"""
    try:
        validated_data = validate_product(req.get_json())
        product_controller.set_context(req, res)
        result = product_controller.store(validated_data)
        res.status(201).json(result)
    except ValidationError as e:
        res.status(400).json({
            "error": "Dados inválidos",
            "details": e.field
        })

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
            res.status(404).json({"error": "Produto não encontrado"})
    except ValidationError as e:
        res.status(400).json({
            "error": "Dados inválidos",
            "details": e.field
        })

@app.delete('/products/:id')
def delete_product(req, res):
    """Remove um produto"""
    product_controller.set_context(req, res)
    product_id = req.params['id']
    result = product_controller.destroy(product_id)
    
    if result:
        res.json({"message": "Produto removido com sucesso"})
    else:
        res.status(404).json({"error": "Produto não encontrado"})

@app.get('/products/search')
def search_products(req, res):
    """Busca produtos"""
    product_controller.set_context(req, res)
    result = product_controller.search()
    res.json(result)

# Rota de status
@app.get('/')
def home(req, res):
    res.json({
        "message": "API com Prisma - PYREST-FRAMEWORK",
        "version": "2.0.0",
        "database": "PostgreSQL + Prisma" if db_manager.client else "In-Memory",
        "endpoints": {
            "users": "/users",
            "products": "/products",
            "auth": "/login, /register"
        }
    })

# Rota para informações do banco
@app.get('/database/status')
def database_status(req, res):
    res.json({
        "connected": db_manager.client is not None,
        "database_url": DATABASE_URL,
        "provider": "postgresql"
    })

if __name__ == '__main__':
    print("🚀 API com Prisma iniciando...")
    print("📚 Endpoints disponíveis:")
    print("   GET  / - Status da API")
    print("   GET  /database/status - Status do banco")
    print("   GET  /users - Lista usuários")
    print("   POST /users - Cria usuário")
    print("   GET  /users/:id - Obtém usuário")
    print("   PUT  /users/:id - Atualiza usuário")
    print("   DELETE /users/:id - Remove usuário")
    print("   POST /login - Login")
    print("   POST /register - Registro")
    print("   GET  /products - Lista produtos")
    print("   POST /products - Cria produto")
    print("   GET  /products/:id - Obtém produto")
    print("   PUT  /products/:id - Atualiza produto")
    print("   DELETE /products/:id - Remove produto")
    print("   GET  /products/search?q=termo - Busca produtos")
    
    try:
        app.listen(port=3000, debug=True)
    finally:
        # Desconecta do banco ao finalizar
        if db_manager:
            db_manager.disconnect() 