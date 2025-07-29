# PYREST-FRAMEWORK v2.0.1 - Documentação Técnica

## Visão Geral

O **PYREST-FRAMEWORK** é um framework Python moderno e robusto para criação de APIs REST, inspirado no Express.js do Node.js. Desenvolvido especificamente para projetos acadêmicos de Análise e Desenvolvimento de Sistemas (ADS), oferece uma experiência de desenvolvimento profissional com arquitetura MVC completa.

### Características Principais

- ✅ **Arquitetura MVC Completa**: Controllers, Services, Models e Repositories
- ✅ **Integração com Prisma ORM**: Suporte a PostgreSQL, MySQL e SQLite
- ✅ **Sistema de Validação Robusto**: Validação automática de dados
- ✅ **CLI Avançado**: Criação automática de projetos com estrutura completa
- ✅ **Middlewares Avançados**: CORS, logging, auth, rate limiting
- ✅ **Sintaxe Familiar**: Inspirado no Express.js
- ✅ **Documentação Extensa**: Guias completos e exemplos
- ✅ **Sistema de Testes**: Cobertura abrangente
- ✅ **Exemplos Práticos**: Código real e funcional

## Índice

1. [Instalação](#instalação)
2. [Primeiros Passos](#primeiros-passos)
3. [Conceitos Fundamentais](#conceitos-fundamentais)
4. [Roteamento](#roteamento)
5. [Request e Response](#request-e-response)
6. [Middlewares](#middlewares)
7. [Tratamento de Erros](#tratamento-de-erros)
8. [CLI (Command Line Interface)](#cli-command-line-interface)
9. [Exemplos Avançados](#exemplos-avançados)
10. [Testes](#testes)
11. [Deploy](#deploy)
12. [Referência da API](#referência-da-api)

---

## Instalação

### Requisitos do Sistema

- **Python**: 3.7 ou superior
- **Sistema Operacional**: Windows, macOS, Linux
- **Memória**: Mínimo 128MB RAM
- **Espaço**: Mínimo 50MB de espaço em disco

### Instalação via pip

```bash
pip install pyrest-framework
```

### Instalação em Desenvolvimento

```bash
git clone https://github.com/mamadusamadev/pyrest-framework.git
cd pyrest-framework
pip install -e .
```

### Verificação da Instalação

```bash
# Testa a instalação
python install_and_test.py

# Ou usa o CLI
pyrest info
```

---

## Primeiros Passos

### Hello World

```python
from pyrest import create_app

# Cria a aplicação
app = create_app()

# Define uma rota
@app.get('/')
def hello_world(req, res):
    res.json({
        "message": "Hello, PYREST-FRAMEWORK!",
        "version": "2.0.1"
    })

# Inicia o servidor
if __name__ == '__main__':
    app.listen(port=3000, debug=True)
```

### Usando o CLI

```bash
# Cria um novo projeto
pyrest create minha-api

# Entra no projeto
cd minha-api

# Inicia o servidor
pyrest serve --debug

# Ou inicia um servidor de exemplo
pyrest serve --quick
```

---

## Conceitos Fundamentais

### Arquitetura do Framework

O PYREST-FRAMEWORK segue uma arquitetura modular e extensível:

```
┌─────────────────┐
│   Application   │  ← Classe principal
├─────────────────┤
│    Routes       │  ← Sistema de roteamento
├─────────────────┤
│   Middlewares   │  ← Camada de middlewares
├─────────────────┤
│   Request/Res   │  ← Objetos HTTP
└─────────────────┘
```

### Fluxo de Requisição

1. **Requisição HTTP** chega ao servidor
2. **Middlewares** são executados em sequência
3. **Roteamento** encontra o handler correto
4. **Handler** processa a requisição
5. **Response** é enviada de volta

### Componentes Principais

#### PyRestFramework (App)
- Classe principal do framework
- Gerencia rotas, middlewares e configurações
- Responsável pelo ciclo de vida da aplicação

#### Route
- Representa uma rota HTTP
- Suporte a parâmetros dinâmicos (`:id`)
- Matching baseado em regex

#### Request
- Objeto que representa a requisição HTTP
- Parsing automático de JSON e form data
- Acesso a headers, query params, body

#### Response
- Objeto que representa a resposta HTTP
- Múltiplos formatos de resposta (JSON, HTML, XML)
- Headers de segurança e cache

---

## Roteamento

### Métodos HTTP Suportados

```python
@app.get('/users')           # GET
@app.post('/users')          # POST
@app.put('/users/:id')       # PUT
@app.delete('/users/:id')    # DELETE
@app.patch('/users/:id')     # PATCH
@app.options('/users')       # OPTIONS
```

### Parâmetros de Rota

```python
@app.get('/users/:id')
def get_user(req, res):
    user_id = req.params['id']  # Acessa o parâmetro
    res.json({"id": user_id})

# Requisição: GET /users/123
# Resultado: {"id": "123"}
```

### Query Parameters

```python
@app.get('/users')
def get_users(req, res):
    page = req.get_query('page', '1')
    limit = req.get_query('limit', '10')
    
    res.json({
        "page": page,
        "limit": limit
    })

# Requisição: GET /users?page=2&limit=20
```

### Múltiplas Rotas

```python
@app.get('/')
@app.get('/home')
def home(req, res):
    res.json({"message": "Welcome!"})
```

---

## Request e Response

### Objeto Request

#### Propriedades Principais

```python
req.method        # Método HTTP (GET, POST, etc.)
req.path          # Caminho da requisição
req.headers       # Headers HTTP (dict)
req.body          # Corpo da requisição (string)
req.params        # Parâmetros de rota (dict)
req.query         # Query parameters (dict)
req.json_data     # Dados JSON parseados (dict)
req.form_data     # Dados de formulário (dict)
```

#### Métodos Úteis

```python
# Headers
user_agent = req.get_header('user-agent', 'Unknown')

# Query Parameters
page = req.get_query('page', '1')

# Route Parameters
user_id = req.get_param('id')

# JSON Data
data = req.get_json()
name = req.get_json('name', 'Default')

# Form Data
form_data = req.get_form()
email = req.get_form('email')

# Verificações
if req.is_json():
    data = req.get_json()

if req.is_secure():
    # Requisição HTTPS
```

### Objeto Response

#### Métodos de Resposta

```python
# JSON Response
res.json({"message": "Success"})

# Text Response
res.send("Hello World")

# HTML Response
res.html("<h1>Hello</h1>")

# XML Response
res.xml("<root><message>Hello</message></root>")

# File Response
res.file(content, "file.txt", "text/plain")

# Redirect
res.redirect('/new-page')
```

#### Headers e Status

```python
# Status Code
res.status(201).json(data)

# Headers
res.header('Content-Type', 'application/json')
res.header('Authorization', 'Bearer token')

# Multiple Headers
res.headers_dict({
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache'
})
```

#### Cookies e CORS

```python
# Cookies
res.cookie('session', 'abc123', max_age=3600, secure=True)
res.clear_cookie('session')

# CORS
res.cors(origin='https://example.com', credentials=True)
```

---

## Middlewares

### Middlewares Incluídos

#### CORS (Cross-Origin Resource Sharing)

```python
from pyrest import Middlewares

app.use(Middlewares.cors())
app.use(Middlewares.cors(
    origin='https://example.com',
    credentials=True
))
```

#### Logger

```python
app.use(Middlewares.logger())        # combined
app.use(Middlewares.logger('dev'))   # desenvolvimento
app.use(Middlewares.logger('common')) # comum
```

#### Body Parser

```python
app.use(Middlewares.body_parser())
app.use(Middlewares.json_parser())
app.use(Middlewares.urlencoded())
```

#### Security Headers

```python
app.use(Middlewares.security_headers())
```

#### Rate Limiting

```python
app.use(Middlewares.rate_limit(
    max_requests=100,
    window_ms=60000
))
```

#### Authentication

```python
app.use(Middlewares.auth_required())
```

#### Static Files

```python
app.use(Middlewares.static_files('public', '/static'))
```

### Middleware Personalizado

```python
def custom_middleware(req, res):
    # Adiciona timestamp à requisição
    req.timestamp = time.time()
    
    # Continua a execução
    return True

app.use(custom_middleware)
```

### Middleware que Para a Execução

```python
def auth_middleware(req, res):
    token = req.get_header('authorization')
    
    if not token:
        res.status(401).json({
            "error": "Unauthorized"
        })
        return False  # Para a execução
    
    return True  # Continua a execução

app.use(auth_middleware)
```

---

## Tratamento de Erros

### Handlers de Erro Personalizados

```python
@app.error_handler(404)
def not_found(req, res):
    res.json({
        "error": "Not Found",
        "message": f"Route '{req.path}' not found"
    })

@app.error_handler(500)
def server_error(req, res):
    res.json({
        "error": "Internal Server Error",
        "message": "Something went wrong"
    })
```

### Tratamento de Exceções

```python
@app.get('/users/:id')
def get_user(req, res):
    try:
        user_id = int(req.params['id'])
        user = find_user(user_id)
        
        if not user:
            res.status(404).json({
                "error": "User not found"
            })
            return
        
        res.json(user)
        
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID format"
        })
    except Exception as e:
        res.status(500).json({
            "error": "Internal server error",
            "message": str(e)
        })
```

### Middleware de Tratamento Global

```python
def error_handler_middleware(req, res):
    try:
        # Continua a execução
        pass
    except Exception as e:
        res.status(500).json({
            "error": "Internal Server Error",
            "message": str(e)
        })
        return False

app.use(error_handler_middleware)
```

---

## CLI (Command Line Interface)

### Comandos Disponíveis

#### `pyrest create <nome>`

Cria um novo projeto com estrutura completa.

```bash
# Criação básica
pyrest create minha-api

# Com diretório específico
pyrest create minha-api -o /path/to/output
```

**Estrutura criada:**
```
minha-api/
├── app.py              # Aplicação principal
├── README.md           # Documentação
├── requirements.txt    # Dependências
├── .gitignore         # Git ignore
├── routes/            # Rotas organizadas
├── middlewares/       # Middlewares customizados
├── models/            # Modelos de dados
├── utils/             # Utilitários
└── tests/             # Testes
```

#### `pyrest serve`

Inicia um servidor PyRest.

```bash
# Carrega app.py (padrão)
pyrest serve

# Carrega arquivo específico
pyrest serve app.py

# Servidor de exemplo
pyrest serve --quick

# Configurações específicas
pyrest serve --port 8080 --host 0.0.0.0 --debug
```

#### `pyrest info`

Mostra informações sobre o framework.

```bash
pyrest info
```

### Opções do Comando Serve

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `--port` | Porta do servidor | 3000 |
| `--host` | Host do servidor | localhost |
| `--debug` | Modo debug | False |
| `--quick` | Servidor de exemplo | False |

---

## Exemplos Avançados

### API REST Completa

```python
from pyrest import create_app, Middlewares

app = create_app()

# Middlewares
app.use(Middlewares.cors())
app.use(Middlewares.logger('dev'))
app.use(Middlewares.json_parser())

# Simula banco de dados
users = []

# GET /users
@app.get('/users')
def get_users(req, res):
    page = int(req.get_query('page', '1'))
    limit = int(req.get_query('limit', '10'))
    
    start = (page - 1) * limit
    end = start + limit
    
    paginated_users = users[start:end]
    
    res.json({
        "users": paginated_users,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(users)
        }
    })

# POST /users
@app.post('/users')
def create_user(req, res):
    data = req.json_data
    
    if not data or 'name' not in data:
        res.status(400).json({
            "error": "Name is required"
        })
        return
    
    new_user = {
        "id": len(users) + 1,
        "name": data['name'],
        "email": data.get('email', '')
    }
    
    users.append(new_user)
    
    res.status(201).json(new_user)

# GET /users/:id
@app.get('/users/:id')
def get_user(req, res):
    try:
        user_id = int(req.params['id'])
        user = next((u for u in users if u['id'] == user_id), None)
        
        if user:
            res.json(user)
        else:
            res.status(404).json({
                "error": "User not found"
            })
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID"
        })

# PUT /users/:id
@app.put('/users/:id')
def update_user(req, res):
    try:
        user_id = int(req.params['id'])
        data = req.json_data
        
        user_index = next((i for i, u in enumerate(users) 
                          if u['id'] == user_id), None)
        
        if user_index is None:
            res.status(404).json({
                "error": "User not found"
            })
            return
        
        users[user_index].update(data)
        users[user_index]['id'] = user_id
        
        res.json(users[user_index])
        
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID"
        })

# DELETE /users/:id
@app.delete('/users/:id')
def delete_user(req, res):
    try:
        user_id = int(req.params['id'])
        
        user_index = next((i for i, u in enumerate(users) 
                          if u['id'] == user_id), None)
        
        if user_index is None:
            res.status(404).json({
                "error": "User not found"
            })
            return
        
        deleted_user = users.pop(user_index)
        
        res.json({
            "message": "User deleted",
            "user": deleted_user
        })
        
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID"
        })

if __name__ == '__main__':
    app.listen(port=3000, debug=True)
```

### Autenticação com JWT

```python
import jwt
import hashlib
from datetime import datetime, timedelta
from pyrest import create_app, Middlewares

app = create_app()

# Configurações
JWT_SECRET = "your-secret-key"
JWT_EXPIRATION = 3600

# Middleware de autenticação
def auth_middleware(req, res):
    # Rotas públicas
    public_routes = ['/login', '/register']
    
    if req.path in public_routes:
        return True
    
    # Verifica token
    auth_header = req.get_header('authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        res.status(401).json({
            "error": "Token required"
        })
        return False
    
    token = auth_header[7:]
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        req.user = payload
        return True
    except:
        res.status(401).json({
            "error": "Invalid token"
        })
        return False

app.use(auth_middleware)

# Login
@app.post('/login')
def login(req, res):
    data = req.json_data
    
    # Validação básica
    if not data or 'username' not in data or 'password' not in data:
        res.status(400).json({
            "error": "Username and password required"
        })
        return
    
    # Aqui você faria a validação real
    if data['username'] == 'admin' and data['password'] == 'password':
        payload = {
            'user_id': 1,
            'username': data['username'],
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION)
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        
        res.json({
            "message": "Login successful",
            "token": token,
            "expires_in": JWT_EXPIRATION
        })
    else:
        res.status(401).json({
            "error": "Invalid credentials"
        })

# Rota protegida
@app.get('/profile')
def get_profile(req, res):
    res.json({
        "user_id": req.user['user_id'],
        "username": req.user['username']
    })

if __name__ == '__main__':
    app.listen(port=3000, debug=True)
```

---

## Testes

### Executando Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=pyrest

# Testes específicos
pytest tests/test_core.py -v

# Com relatório HTML
pytest --cov=pyrest --cov-report=html
```

### Escrevendo Testes

```python
import unittest
from unittest.mock import Mock
from pyrest import create_app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
    
    def test_home_route(self):
        # Simula requisição
        req = Mock()
        req.method = 'GET'
        req.path = '/'
        
        res = Mock()
        res.json = Mock()
        
        # Executa handler
        @self.app.get('/')
        def home(req, res):
            res.json({"message": "Hello"})
        
        # Verifica se rota foi registrada
        self.assertEqual(len(self.app.routes), 1)
        route = self.app.routes[0]
        self.assertEqual(route.method, 'GET')
        self.assertEqual(route.path, '/')
```

### Testes de Integração

```python
import requests

def test_api_integration():
    # Inicia servidor em thread separada
    import threading
    import time
    
    def start_server():
        app.listen(port=3001)
    
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(1)  # Aguarda servidor iniciar
    
    # Testa API
    response = requests.get('http://localhost:3001/')
    assert response.status_code == 200
    assert response.json()['message'] == 'Hello'
```

---

## Deploy

### Ambiente de Desenvolvimento

```bash
# Instalação
pip install -r requirements.txt

# Execução
python app.py

# Ou usando CLI
pyrest serve --debug
```

### Ambiente de Produção

```bash
# Instalação
pip install pyrest-framework

# Execução
pyrest serve --host 0.0.0.0 --port 80
```

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["python", "app.py"]
```

### Nginx (Proxy Reverso)

```nginx
server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service

```ini
[Unit]
Description=PyRest API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/api
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Referência da API

Para documentação completa da API, consulte:
- [API Reference](API_REFERENCE.md) - Referência detalhada de todas as classes e métodos
- [Changelog](CHANGELOG.md) - Histórico de versões e mudanças

### Classes Principais

#### PyRestFramework
- `get(path, handler=None)` - Define rota GET
- `post(path, handler=None)` - Define rota POST
- `put(path, handler=None)` - Define rota PUT
- `delete(path, handler=None)` - Define rota DELETE
- `patch(path, handler=None)` - Define rota PATCH
- `options(path, handler=None)` - Define rota OPTIONS
- `use(middleware)` - Adiciona middleware
- `error_handler(status_code)` - Define handler de erro
- `listen(port=3000, host='localhost', debug=False)` - Inicia servidor

#### Request
- `get_header(name, default=None)` - Obtém header
- `get_query(name, default=None)` - Obtém query parameter
- `get_param(name, default=None)` - Obtém parâmetro de rota
- `get_json(key=None, default=None)` - Obtém dados JSON
- `get_form(key=None, default=None)` - Obtém dados de formulário
- `is_json()` - Verifica se é JSON
- `is_form()` - Verifica se é form data
- `is_secure()` - Verifica se é HTTPS

#### Response
- `status(code)` - Define status code
- `header(key, value)` - Define header
- `json(data, indent=None, ensure_ascii=False)` - Resposta JSON
- `send(data)` - Resposta texto
- `html(content)` - Resposta HTML
- `xml(content)` - Resposta XML
- `file(content, filename, mimetype=None)` - Resposta arquivo
- `redirect(url, permanent=False)` - Redirecionamento
- `cookie(name, value, **options)` - Define cookie
- `cors(**options)` - Headers CORS

#### Middlewares
- `cors(**options)` - Middleware CORS
- `logger(format='combined')` - Middleware de logging
- `body_parser()` - Middleware body parser
- `json_parser()` - Middleware JSON parser
- `urlencoded()` - Middleware URL encoded
- `static_files(directory, prefix='/static')` - Middleware static files
- `rate_limit(max_requests=100, window_ms=60000)` - Middleware rate limiting
- `auth_required()` - Middleware de autenticação
- `error_handler()` - Middleware de tratamento de erros
- `security_headers()` - Middleware de headers de segurança

---

## Suporte e Comunidade

### Recursos Adicionais

- **GitHub**: [https://github.com/mamadusamadev/pyrest-framework](https://github.com/mamadusamadev/pyrest-framework)
- **Issues**: Para reportar bugs ou solicitar features
- **Discussions**: Para dúvidas e discussões
- **Wiki**: Documentação adicional e tutoriais

### Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](../LICENSE) para detalhes.

---

## Conclusão

O PYREST-FRAMEWORK v2.0.1 oferece uma solução completa e profissional para desenvolvimento de APIs REST em Python. Com sua arquitetura MVC moderna, integração com Prisma ORM, sistema de validação robusto e CLI avançado, é ideal tanto para aprendizado quanto para projetos reais em produção.

### Principais Melhorias da v2.0.1

- ✅ **Arquitetura MVC Completa**: Separação clara entre Controllers, Services, Models e Repositories
- ✅ **Integração com Prisma**: Suporte nativo a PostgreSQL, MySQL e SQLite
- ✅ **Sistema de Validação**: Validação automática de dados com múltiplos validadores
- ✅ **CLI Avançado**: Criação automática de projetos com estrutura profissional
- ✅ **Fallback Inteligente**: Funciona com ou sem banco de dados
- ✅ **Documentação Completa**: Guias detalhados para todas as funcionalidades

Para começar rapidamente:

```bash
# Instalação básica
pip install pyrest-framework

# Instalação com suporte a banco de dados
pip install pyrest-framework[database]

# Criação de projeto com estrutura MVC completa
pyrest create minha-api

# Execução
cd minha-api
pyrest serve --debug
```

**Happy coding! 🚀**
