"""
Utilidades e funções auxiliares do PYREST-FRAMEWORK
"""

from .core import PyRestFramework

def create_app():
    """
    Cria uma nova instância do framework PYREST
    
    Returns:
        PyRestFramework: Nova instância do framework
    
    Example:
        >>> from pyrest import create_app
        >>> app = create_app()
        >>> @app.get('/')
        >>> def home(req, res):
        ...     res.json({"message": "Hello World!"})
    """
    return PyRestFramework()

def quick_start(port: int = 3000, host: str = 'localhost', debug: bool = True):
    """
    Inicia um servidor PyRest com uma rota de exemplo
    Útil para testes rápidos e demonstrações
    
    Args:
        port (int): Porta para o servidor (padrão: 3000)
        host (str): Host para o servidor (padrão: 'localhost') 
        debug (bool): Modo debug (padrão: True)
    
    Example:
        >>> from pyrest.utils import quick_start
        >>> quick_start(8080)  # Inicia servidor na porta 8080
    """
    app = create_app()
    
    @app.get('/')
    def home(req, res):
        res.json({
            "message": "🚀 PyRest Framework está funcionando!",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "info": "/info"
            },
            "docs": "https://github.com/mamadusamadev/pyrest-framework"
        })
    
    @app.get('/health')
    def health(req, res):
        res.json({
            "status": "OK",
            "service": "PyRest Framework",
            "uptime": "Running"
        })
    
    @app.get('/info')
    def info(req, res):
        import sys
        import platform
        
        res.json({
            "framework": "PyRest Framework",
            "version": "1.0.0",
            "python_version": sys.version,
            "platform": platform.platform(),
            "endpoints_registered": len(app.routes),
            "middlewares_registered": len(app.middlewares)
        })
    
    print("🚀 PyRest Quick Start - Servidor de exemplo iniciado!")
    print(f"📍 Acesse: http://{host}:{port}")
    print("📚 Endpoints disponíveis:")
    print(f"   • GET http://{host}:{port}/")
    print(f"   • GET http://{host}:{port}/health") 
    print(f"   • GET http://{host}:{port}/info")
    
    app.listen(port=port, host=host, debug=debug)

def version_info():
    """
    Retorna informações detalhadas sobre a versão do framework
    
    Returns:
        dict: Informações de versão
    """
    import sys
    import platform
    from . import __version__, __author__, __license__
    
    return {
        "pyrest_version": __version__,
        "author": __author__,
        "license": __license__,
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "architecture": platform.architecture()[0]
    }

def print_routes(app: PyRestFramework):
    """
    Imprime todas as rotas registradas no app
    
    Args:
        app (PyRestFramework): Instância do framework
    """
    if not app.routes:
        print("📭 Nenhuma rota registrada")
        return
    
    print(f"📋 Rotas registradas ({len(app.routes)}):")
    print("=" * 50)
    
    methods_colors = {
        'GET': '\033[92m',     # Verde
        'POST': '\033[94m',    # Azul
        'PUT': '\033[93m',     # Amarelo
        'DELETE': '\033[91m',  # Vermelho
        'PATCH': '\033[95m',   # Magenta
        'OPTIONS': '\033[96m'  # Ciano
    }
    reset_color = '\033[0m'
    
    for i, route in enumerate(app.routes, 1):
        method_color = methods_colors.get(route.method, '')
        print(f"{i:2d}. {method_color}{route.method:7s}{reset_color} {route.path}")
    
    print("=" * 50)

def benchmark_app(app: PyRestFramework, endpoint: str = '/', num_requests: int = 100):
    """
    Executa um benchmark básico do app
    
    Args:
        app (PyRestFramework): Instância do framework
        endpoint (str): Endpoint para testar (padrão: '/')
        num_requests (int): Número de requisições (padrão: 100)
    
    Returns:
        dict: Resultados do benchmark
    """
    import time
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Inicia servidor em thread separada
    server_thread = threading.Thread(
        target=lambda: app.listen(port=8999, host='localhost'),
        daemon=True
    )
    server_thread.start()
    time.sleep(1)  # Aguarda servidor iniciar
    
    def make_request():
        import urllib.request
        try:
            start = time.time()
            with urllib.request.urlopen(f'http://localhost:8999{endpoint}') as response:
                end = time.time()
                return {
                    'success': response.status == 200,
                    'response_time': end - start,
                    'status_code': response.status
                }
        except Exception as e:
            return {
                'success': False,
                'response_time': 0,
                'error': str(e)
            }
    
    print(f"🔥 Executando benchmark: {num_requests} requisições para {endpoint}")
    
    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        for future in as_completed(futures):
            results.append(future.result())
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Análise dos resultados
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    response_times = [r['response_time'] for r in successful]
    
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
    else:
        avg_response_time = min_response_time = max_response_time = 0
    
    benchmark_results = {
        'total_requests': num_requests,
        'successful_requests': len(successful),
        'failed_requests': len(failed),
        'success_rate': len(successful) / num_requests * 100,
        'total_time': total_time,
        'requests_per_second': num_requests / total_time,
        'avg_response_time': avg_response_time,
        'min_response_time': min_response_time,
        'max_response_time': max_response_time
    }
    
    # Imprime resultados
    print("\n📊 Resultados do Benchmark:")
    print("=" * 40)
    print(f"Total de requisições:     {benchmark_results['total_requests']}")
    print(f"Requisições bem-sucedidas: {benchmark_results['successful_requests']}")
    print(f"Requisições falhadas:     {benchmark_results['failed_requests']}")
    print(f"Taxa de sucesso:          {benchmark_results['success_rate']:.1f}%")
    print(f"Tempo total:              {benchmark_results['total_time']:.2f}s")
    print(f"Requisições por segundo:  {benchmark_results['requests_per_second']:.2f}")
    print(f"Tempo médio de resposta:  {benchmark_results['avg_response_time']*1000:.2f}ms")
    print(f"Tempo mín de resposta:    {benchmark_results['min_response_time']*1000:.2f}ms")
    print(f"Tempo máx de resposta:    {benchmark_results['max_response_time']*1000:.2f}ms")
    print("=" * 40)
    
    return benchmark_results

def generate_project_template(project_name: str, output_dir: str = "."):
    """
    Gera um template de projeto PyRest com estrutura MVC completa
    
    Args:
        project_name (str): Nome do projeto
        output_dir (str): Diretório de saída (padrão: diretório atual)
    """
    import os
    
    project_path = os.path.join(output_dir, project_name)
    
    # Cria estrutura de diretórios MVC
    directories = [
        project_path,
        os.path.join(project_path, "controllers"),
        os.path.join(project_path, "services"),
        os.path.join(project_path, "models"),
        os.path.join(project_path, "repositories"),
        os.path.join(project_path, "routes"),
        os.path.join(project_path, "middlewares"),
        os.path.join(project_path, "utils"),
        os.path.join(project_path, "tests"),
        os.path.join(project_path, "config")
    ]
    
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
    
    # Template do app principal com estrutura MVC
    main_app_content = f'''"""
{project_name.title()} - PyRest Application
Gerado automaticamente pelo PYREST-FRAMEWORK v2.0.0
Estrutura MVC completa com Controllers, Services e Models
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

# Cria aplicação
app = create_app()

# Middlewares globais
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
        "message": "Bem-vindo ao {project_name.title()}!",
        "framework": "PyRest Framework",
        "version": "2.0.0",
        "architecture": "MVC",
        "endpoints": {{
            "users": "/users",
            "products": "/products",
            "auth": "/login, /register"
        }}
    }})

# Health check
@app.get('/health')
def health_check(req, res):
    res.json({{
        "status": "OK",
        "service": "{project_name}",
        "framework": "PyRest Framework v2.0.0"
    }})

if __name__ == '__main__':
    print("🚀 Iniciando {project_name.title()}...")
    print("📚 Estrutura MVC:")
    print("   • Controllers: Lógica de negócio")
    print("   • Services: Camada de serviços")
    print("   • Models: Modelos de dados")
    print("   • Repositories: Acesso a dados")
    print("   • Routes: Definição de rotas")
    print("   • Middlewares: Interceptadores")
    app.listen(port=3000, debug=True)
'''
    
    # Escreve arquivo principal
    with open(os.path.join(project_path, 'app.py'), 'w', encoding='utf-8') as f:
        f.write(main_app_content)
    
    # Template do README
    readme_content = f'''# {project_name.title()}

Projeto criado com **PYREST-FRAMEWORK v2.0.0** 🚀

Estrutura MVC completa com Controllers, Services e Models.

## Instalação

```bash
pip install pyrest-framework>=2.0.0
```

## Como executar

```bash
python app.py
```

O servidor será iniciado em `http://localhost:3000`

## Endpoints disponíveis

### Autenticação
- `POST /login` - Login de usuário
- `POST /register` - Registro de usuário

### Usuários
- `GET /users` - Lista todos os usuários
- `POST /users` - Cria novo usuário
- `GET /users/:id` - Busca usuário por ID
- `PUT /users/:id` - Atualiza usuário
- `DELETE /users/:id` - Remove usuário

### Produtos
- `GET /products` - Lista todos os produtos
- `POST /products` - Cria novo produto
- `GET /products/:id` - Busca produto por ID
- `PUT /products/:id` - Atualiza produto
- `DELETE /products/:id` - Remove produto
- `GET /products/search?q=termo` - Busca produtos

### Sistema
- `GET /` - Página inicial
- `GET /health` - Health check

## Exemplo de uso

### Criar um item
```bash
curl -X POST http://localhost:3000/api/items \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "Meu Item", "description": "Descrição do item"}}'
```

### Listar items
```bash
curl http://localhost:3000/api/items
```

## Estrutura do projeto

```
{project_name}/
├── app.py              # Aplicação principal
├── routes/             # Rotas organizadas
├── middlewares/        # Middlewares customizados
├── models/             # Modelos de dados
├── utils/              # Utilitários
└── tests/              # Testes
```

---

Desenvolvido com ❤️ usando [PYREST-FRAMEWORK](https://github.com/mamadusamadev/pyrest-framework)
'''
    
    with open(os.path.join(project_path, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # requirements.txt
    requirements_content = '''pyrest-framework>=2.0.1
# Para usar Prisma com PostgreSQL, instale:
# prisma>=0.12.0
# psycopg2-binary>=2.9.0
# python-dotenv>=1.0.0
'''
    
    with open(os.path.join(project_path, 'requirements.txt'), 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    # .gitignore
    gitignore_content = '''__pycache__/
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
MANIFEST

.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

.vscode/
.idea/
*.swp
*.swo
*~

.coverage
htmlcov/
.pytest_cache/
'''
    
    with open(os.path.join(project_path, '.gitignore'), 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    # Arquivos __init__.py vazios
    init_files = [
        os.path.join(project_path, "routes", "__init__.py"),
        os.path.join(project_path, "middlewares", "__init__.py"),
        os.path.join(project_path, "models", "__init__.py"),
        os.path.join(project_path, "utils", "__init__.py"),
        os.path.join(project_path, "tests", "__init__.py")
    ]
    
    for init_file in init_files:
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write('# Este arquivo torna o diretório um pacote Python\n')
    
    print(f"✅ Projeto '{project_name}' criado com sucesso em '{project_path}'!")
    print(f"📁 Estrutura criada:")
    print(f"   • app.py - Aplicação principal")
    print(f"   • README.md - Documentação")
    print(f"   • requirements.txt - Dependências")
    print(f"   • .gitignore - Arquivos ignorados pelo Git")
    print(f"   • routes/ - Diretório para rotas")
    print(f"   • middlewares/ - Diretório para middlewares")
    print(f"   • models/ - Diretório para modelos")
    print(f"   • utils/ - Diretório para utilitários")
    print(f"   • tests/ - Diretório para testes")
    print(f"\n🚀 Para começar:")
    print(f"   cd {project_name}")
    print(f"   python app.py")

# Função auxiliar para validação de dados
def validate_json_schema(data: dict, schema: dict) -> tuple[bool, list]:
    """
    Validação básica de schema JSON
    
    Args:
        data (dict): Dados para validar
        schema (dict): Schema de validação
    
    Returns:
        tuple: (is_valid, errors)
    """
    errors = []
    
    # Campos obrigatórios
    required = schema.get('required', [])
    for field in required:
        if field not in data:
            errors.append(f"Campo '{field}' é obrigatório")
    
    # Tipos de campos
    properties = schema.get('properties', {})
    for field, field_schema in properties.items():
        if field in data:
            expected_type = field_schema.get('type')
            actual_value = data[field]
            
            if expected_type == 'string' and not isinstance(actual_value, str):
                errors.append(f"Campo '{field}' deve ser string")
            elif expected_type == 'number' and not isinstance(actual_value, (int, float)):
                errors.append(f"Campo '{field}' deve ser número")
            elif expected_type == 'boolean' and not isinstance(actual_value, bool):
                errors.append(f"Campo '{field}' deve ser boolean")
            elif expected_type == 'array' and not isinstance(actual_value, list):
                errors.append(f"Campo '{field}' deve ser array")
    
    return len(errors) == 0, errors