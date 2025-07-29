"""
Exemplo básico de API com PYREST-FRAMEWORK
Demonstra as funcionalidades principais do framework
"""

from pyrest import create_app, Middlewares

# Cria a aplicação
app = create_app()

# Adiciona middlewares globais
app.use(Middlewares.cors())
app.use(Middlewares.logger("dev"))
app.use(Middlewares.json_parser())
app.use(Middlewares.security_headers())

# Simula uma base de dados simples
users = [
    {"id": 1, "name": "João Silva", "email": "joao@email.com", "age": 25},
    {"id": 2, "name": "Maria Santos", "email": "maria@email.com", "age": 30},
    {"id": 3, "name": "Pedro Costa", "email": "pedro@email.com", "age": 28}
]

# Rota principal
@app.get('/')
def home(req, res):
    res.json({
        "message": "🚀 Bem-vindo ao PYREST-FRAMEWORK!",
        "version": "1.0.0",
        "endpoints": {
            "users": "/api/users",
            "user_by_id": "/api/users/:id",
            "health": "/health",
            "info": "/info"
        },
        "docs": "https://github.com/mamadusamadev/pyrest-framework"
    })

# Health check
@app.get('/health')
def health_check(req, res):
    res.json({
        "status": "OK",
        "service": "PyRest Basic API",
        "timestamp": "2024-01-01T00:00:00Z"
    })

# Informações do sistema
@app.get('/info')
def system_info(req, res):
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

# API de usuários - GET todos
@app.get('/api/users')
def get_users(req, res):
    # Suporte a query parameters
    limit = req.get_query('limit')
    if limit:
        try:
            limit = int(limit)
            users_response = users[:limit]
        except ValueError:
            res.status(400).json({"error": "Limit deve ser um número"})
            return
    else:
        users_response = users
    
    res.json({
        "users": users_response,
        "total": len(users_response),
        "count": len(users_response)
    })

# API de usuários - GET por ID
@app.get('/api/users/:id')
def get_user_by_id(req, res):
    try:
        user_id = int(req.params['id'])
        user = next((u for u in users if u['id'] == user_id), None)
        
        if user:
            res.json(user)
        else:
            res.status(404).json({
                "error": "User not found",
                "message": f"Usuário com ID {user_id} não encontrado"
            })
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID",
            "message": "ID deve ser um número válido"
        })

# API de usuários - POST criar
@app.post('/api/users')
def create_user(req, res):
    data = req.json_data
    
    # Validação básica
    if not data:
        res.status(400).json({
            "error": "Missing data",
            "message": "Dados do usuário são obrigatórios"
        })
        return
    
    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in data:
            res.status(400).json({
                "error": "Missing field",
                "message": f"Campo '{field}' é obrigatório"
            })
            return
    
    # Verifica se email já existe
    if any(u['email'] == data['email'] for u in users):
        res.status(409).json({
            "error": "Email already exists",
            "message": "Este email já está em uso"
        })
        return
    
    # Cria novo usuário
    new_user = {
        "id": max(u['id'] for u in users) + 1,
        "name": data['name'],
        "email": data['email'],
        "age": data.get('age', 0)
    }
    
    users.append(new_user)
    
    res.status(201).json({
        "message": "Usuário criado com sucesso",
        "user": new_user
    })

# API de usuários - PUT atualizar
@app.put('/api/users/:id')
def update_user(req, res):
    try:
        user_id = int(req.params['id'])
        data = req.json_data
        
        if not data:
            res.status(400).json({
                "error": "Missing data",
                "message": "Dados para atualização são obrigatórios"
            })
            return
        
        # Encontra o usuário
        user_index = next((i for i, u in enumerate(users) if u['id'] == user_id), None)
        
        if user_index is None:
            res.status(404).json({
                "error": "User not found",
                "message": f"Usuário com ID {user_id} não encontrado"
            })
            return
        
        # Atualiza o usuário
        users[user_index].update(data)
        users[user_index]['id'] = user_id  # Mantém o ID original
        
        res.json({
            "message": "Usuário atualizado com sucesso",
            "user": users[user_index]
        })
        
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID",
            "message": "ID deve ser um número válido"
        })

# API de usuários - DELETE
@app.delete('/api/users/:id')
def delete_user(req, res):
    try:
        user_id = int(req.params['id'])
        
        # Encontra o usuário
        user_index = next((i for i, u in enumerate(users) if u['id'] == user_id), None)
        
        if user_index is None:
            res.status(404).json({
                "error": "User not found",
                "message": f"Usuário com ID {user_id} não encontrado"
            })
            return
        
        # Remove o usuário
        deleted_user = users.pop(user_index)
        
        res.json({
            "message": "Usuário removido com sucesso",
            "user": deleted_user
        })
        
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID",
            "message": "ID deve ser um número válido"
        })

# API de usuários - PATCH (atualização parcial)
@app.patch('/api/users/:id')
def patch_user(req, res):
    try:
        user_id = int(req.params['id'])
        data = req.json_data
        
        if not data:
            res.status(400).json({
                "error": "Missing data",
                "message": "Dados para atualização são obrigatórios"
            })
            return
        
        # Encontra o usuário
        user_index = next((i for i, u in enumerate(users) if u['id'] == user_id), None)
        
        if user_index is None:
            res.status(404).json({
                "error": "User not found",
                "message": f"Usuário com ID {user_id} não encontrado"
            })
            return
        
        # Atualiza apenas os campos fornecidos
        for key, value in data.items():
            if key != 'id':  # Não permite alterar o ID
                users[user_index][key] = value
        
        res.json({
            "message": "Usuário atualizado com sucesso",
            "user": users[user_index]
        })
        
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID",
            "message": "ID deve ser um número válido"
        })

# Handler de erro personalizado para 404
@app.error_handler(404)
def not_found_handler(req, res):
    res.json({
        "error": "Not Found",
        "message": f"Rota '{req.path}' não encontrada",
        "available_endpoints": [
            "/",
            "/health",
            "/info",
            "/api/users",
            "/api/users/:id"
        ]
    })

# Handler de erro personalizado para 500
@app.error_handler(500)
def internal_error_handler(req, res):
    res.json({
        "error": "Internal Server Error",
        "message": "Ocorreu um erro interno no servidor"
    })

if __name__ == '__main__':
    print("🚀 Iniciando API básica do PYREST-FRAMEWORK...")
    print("📍 Endpoints disponíveis:")
    print("   • GET  / - Página inicial")
    print("   • GET  /health - Health check")
    print("   • GET  /info - Informações do sistema")
    print("   • GET  /api/users - Lista todos os usuários")
    print("   • GET  /api/users/:id - Busca usuário por ID")
    print("   • POST /api/users - Cria novo usuário")
    print("   • PUT  /api/users/:id - Atualiza usuário")
    print("   • PATCH /api/users/:id - Atualização parcial")
    print("   • DELETE /api/users/:id - Remove usuário")
    print("\n🔥 Servidor rodando em http://localhost:3000")
    
    app.listen(port=3000, debug=True)
