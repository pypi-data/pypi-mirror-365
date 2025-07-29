# Referência da API - PYREST-FRAMEWORK

## Índice

1. [Classe PyRestFramework](#pyrestframework)
2. [Classe Request](#request)
3. [Classe Response](#response)
4. [Classe Route](#route)
5. [Middlewares](#middlewares)
6. [Utilitários](#utilitários)
7. [CLI](#cli)

---

## PyRestFramework

A classe principal do framework.

### Construtor

```python
app = PyRestFramework()
```

### Métodos de Roteamento

#### `get(path, handler=None)`
Define uma rota GET.

```python
@app.get('/users')
def get_users(req, res):
    res.json({"users": []})

# Ou usando chamada direta
app.get('/users', get_users)
```

#### `post(path, handler=None)`
Define uma rota POST.

```python
@app.post('/users')
def create_user(req, res):
    data = req.json_data
    res.status(201).json({"created": data})
```

#### `put(path, handler=None)`
Define uma rota PUT.

```python
@app.put('/users/:id')
def update_user(req, res):
    user_id = req.params['id']
    res.json({"updated": user_id})
```

#### `delete(path, handler=None)`
Define uma rota DELETE.

```python
@app.delete('/users/:id')
def delete_user(req, res):
    user_id = req.params['id']
    res.json({"deleted": user_id})
```

#### `patch(path, handler=None)`
Define uma rota PATCH.

```python
@app.patch('/users/:id')
def patch_user(req, res):
    user_id = req.params['id']
    res.json({"patched": user_id})
```

#### `options(path, handler=None)`
Define uma rota OPTIONS.

```python
@app.options('/users')
def options_users(req, res):
    res.header("Allow", "GET, POST, PUT, DELETE")
    res.send("")
```

### Middlewares

#### `use(middleware)`
Adiciona um middleware global.

```python
app.use(Middlewares.cors())
app.use(Middlewares.logger())
```

### Handlers de Erro

#### `error_handler(status_code)`
Define um handler personalizado para códigos de erro.

```python
@app.error_handler(404)
def not_found(req, res):
    res.json({"error": "Not Found"})

@app.error_handler(500)
def server_error(req, res):
    res.json({"error": "Internal Server Error"})
```

### Servidor

#### `listen(port=3000, host='localhost', debug=False)`
Inicia o servidor HTTP.

```python
app.listen(port=3000, host='localhost', debug=True)
```

#### `run(**kwargs)`
Alias para `listen()`.

```python
app.run(port=3000, debug=True)
```

---

## Request

Representa uma requisição HTTP.

### Propriedades

- `method`: Método HTTP (GET, POST, etc.)
- `path`: Caminho da requisição
- `headers`: Headers da requisição (dict)
- `body`: Corpo da requisição (string)
- `params`: Parâmetros de rota (dict)
- `query`: Query parameters (dict)
- `json_data`: Dados JSON parseados (dict)
- `form_data`: Dados de formulário (dict)

### Métodos

#### `get_header(name, default=None)`
Obtém um header da requisição.

```python
user_agent = req.get_header('user-agent', 'Unknown')
```

#### `get_query(name, default=None)`
Obtém um query parameter.

```python
page = req.get_query('page', '1')
limit = req.get_query('limit', '10')
```

#### `get_param(name, default=None)`
Obtém um parâmetro de rota.

```python
user_id = req.get_param('id')
```

#### `get_json(key=None, default=None)`
Obtém dados JSON.

```python
# Todos os dados
data = req.get_json()

# Campo específico
name = req.get_json('name', 'Default Name')
```

#### `get_form(key=None, default=None)`
Obtém dados de formulário.

```python
# Todos os dados
form_data = req.get_form()

# Campo específico
email = req.get_form('email')
```

#### `is_json()`
Verifica se a requisição contém JSON válido.

```python
if req.is_json():
    data = req.get_json()
```

#### `is_form()`
Verifica se a requisição contém dados de formulário.

```python
if req.is_form():
    form_data = req.get_form()
```

#### `is_secure()`
Verifica se a requisição é HTTPS.

```python
if req.is_secure():
    # Requisição segura
```

#### `get_user_agent()`
Obtém o User-Agent.

```python
user_agent = req.get_user_agent()
```

#### `get_content_type()`
Obtém o Content-Type.

```python
content_type = req.get_content_type()
```

#### `get_content_length()`
Obtém o Content-Length.

```python
length = req.get_content_length()
```

#### `get_remote_addr()`
Obtém o endereço IP do cliente.

```python
client_ip = req.get_remote_addr()
```

#### `accepts(content_type)`
Verifica se o cliente aceita um tipo de conteúdo.

```python
if req.accepts('application/json'):
    res.json(data)
```

---

## Response

Representa uma resposta HTTP.

### Propriedades

- `status_code`: Código de status HTTP (int)
- `headers`: Headers da resposta (dict)
- `body`: Corpo da resposta (string)
- `_sent`: Se a resposta já foi enviada (bool)

### Métodos

#### `status(code)`
Define o código de status.

```python
res.status(201).json(data)
```

#### `header(key, value)`
Define um header.

```python
res.header('Content-Type', 'application/json')
res.header('Authorization', 'Bearer token')
```

#### `headers_dict(headers)`
Define múltiplos headers.

```python
res.headers_dict({
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache'
})
```

#### `json(data, indent=None, ensure_ascii=False)`
Envia resposta em JSON.

```python
res.json({"message": "Success"})
res.json(data, indent=2)
```

#### `send(data)`
Envia resposta em texto plano.

```python
res.send("Hello World")
res.send(123)
res.send(True)
```

#### `html(html_content)`
Envia resposta em HTML.

```python
res.html("<h1>Hello World</h1>")
```

#### `xml(xml_content)`
Envia resposta em XML.

```python
res.xml("<root><message>Hello</message></root>")
```

#### `file(content, filename, mimetype=None)`
Envia arquivo como resposta.

```python
with open('file.txt', 'rb') as f:
    content = f.read()
res.file(content, 'file.txt', 'text/plain')
```

#### `redirect(url, permanent=False)`
Redireciona para outra URL.

```python
res.redirect('/new-page')  # 302
res.redirect('/new-page', permanent=True)  # 301
```

#### `cookie(name, value, max_age=None, path='/', domain=None, secure=False, httponly=False, samesite=None)`
Define um cookie.

```python
res.cookie('session', 'abc123', max_age=3600, secure=True)
```

#### `clear_cookie(name, path='/', domain=None)`
Remove um cookie.

```python
res.clear_cookie('session')
```

#### `cors(origin='*', methods='GET, POST, PUT, DELETE, OPTIONS', headers='Content-Type, Authorization', credentials=False)`
Configura headers CORS.

```python
res.cors(origin='https://example.com', credentials=True)
```

#### `cache_control(max_age=None, no_cache=False, no_store=False, public=False, private=False)`
Define headers de controle de cache.

```python
res.cache_control(max_age=3600, public=True)
```

#### `etag(value, weak=False)`
Define ETag.

```python
res.etag('abc123')
```

#### `last_modified(date)`
Define Last-Modified.

```python
res.last_modified('Wed, 21 Oct 2015 07:28:00 GMT')
```

#### `content_encoding(encoding)`
Define encoding do content.

```python
res.content_encoding('gzip')
```

#### `security_headers(csp=None, xss_protection=True, content_type_options=True, frame_options='DENY', hsts=False, hsts_max_age=31536000)`
Define headers de segurança.

```python
res.security_headers(
    csp="default-src 'self'",
    hsts=True
)
```

#### `get_content_length()`
Obtém o tamanho do conteúdo.

```python
length = res.get_content_length()
```

#### `get_header(name, default=None)`
Obtém um header.

```python
content_type = res.get_header('Content-Type')
```

#### `remove_header(name)`
Remove um header.

```python
res.remove_header('Cache-Control')
```

#### `is_sent()`
Verifica se a resposta já foi enviada.

```python
if not res.is_sent():
    res.json(data)
```

---

## Route

Representa uma rota HTTP.

### Propriedades

- `method`: Método HTTP (string)
- `path`: Caminho da rota (string)
- `handler`: Função handler (callable)
- `pattern`: Padrão regex compilado (re.Pattern)

### Métodos

#### `matches(method, path)`
Verifica se a rota corresponde ao método e caminho.

```python
if route.matches('GET', '/users/123'):
    # Rota corresponde
```

#### `extract_params(path)`
Extrai parâmetros da URL.

```python
params = route.extract_params('/users/123')
# Retorna: {'id': '123'}
```

---

## Middlewares

### CORS

```python
from pyrest import Middlewares

app.use(Middlewares.cors())
app.use(Middlewares.cors(origin='https://example.com', credentials=True))
```

### Logger

```python
app.use(Middlewares.logger())  # combined
app.use(Middlewares.logger('dev'))
app.use(Middlewares.logger('common'))
```

### Body Parser

```python
app.use(Middlewares.body_parser())
```

### JSON Parser

```python
app.use(Middlewares.json_parser())
```

### URL Encoded

```python
app.use(Middlewares.urlencoded())
```

### Static Files

```python
app.use(Middlewares.static_files('public', '/static'))
```

### Rate Limit

```python
app.use(Middlewares.rate_limit(max_requests=100, window_ms=60000))
```

### Auth Required

```python
app.use(Middlewares.auth_required())
```

### Error Handler

```python
app.use(Middlewares.error_handler())
```

### Security Headers

```python
app.use(Middlewares.security_headers())
```

---

## Utilitários

### `create_app()`

Cria uma nova instância do framework.

```python
from pyrest import create_app

app = create_app()
```

### `quick_start(port=3000, host='localhost', debug=True)`

Inicia um servidor com rotas de exemplo.

```python
from pyrest.utils import quick_start

quick_start(port=8080, debug=True)
```

### `version_info()`

Retorna informações de versão.

```python
from pyrest.utils import version_info

info = version_info()
print(info)
```

### `print_routes(app)`

Imprime todas as rotas registradas.

```python
from pyrest.utils import print_routes

print_routes(app)
```

### `benchmark_app(app, endpoint='/', num_requests=100)`

Executa benchmark do app.

```python
from pyrest.utils import benchmark_app

results = benchmark_app(app, num_requests=1000)
```

### `generate_project_template(project_name, output_dir='.')`

Gera template de projeto.

```python
from pyrest.utils import generate_project_template

generate_project_template('minha-api')
```

### `validate_json_schema(data, schema)`

Validação básica de schema JSON.

```python
from pyrest.utils import validate_json_schema

schema = {
    'required': ['name', 'email'],
    'properties': {
        'name': {'type': 'string'},
        'email': {'type': 'string'},
        'age': {'type': 'number'}
    }
}

is_valid, errors = validate_json_schema(data, schema)
```

---

## CLI

### Comandos

#### `pyrest create <nome>`

Cria um novo projeto.

```bash
pyrest create minha-api
pyrest create minha-api -o /path/to/output
```

#### `pyrest serve`

Inicia um servidor.

```bash
pyrest serve                    # Carrega app.py
pyrest serve app.py            # Carrega arquivo específico
pyrest serve --quick           # Servidor de exemplo
pyrest serve --port 8080       # Porta específica
pyrest serve --host 0.0.0.0    # Host específico
pyrest serve --debug           # Modo debug
```

#### `pyrest info`

Mostra informações do framework.

```bash
pyrest info
```

### Exemplos de Uso

```bash
# Criar novo projeto
pyrest create blog-api

# Entrar no projeto
cd blog-api

# Instalar dependências
pip install -r requirements.txt

# Executar
python app.py

# Ou usar CLI
pyrest serve --debug
```
