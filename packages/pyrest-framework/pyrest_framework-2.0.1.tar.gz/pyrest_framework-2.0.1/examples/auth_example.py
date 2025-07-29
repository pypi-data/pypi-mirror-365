"""
Exemplo de autenticação com PYREST-FRAMEWORK
Demonstra JWT, middleware de autenticação e rotas protegidas
"""

import jwt
import hashlib
import time
from datetime import datetime, timedelta
from pyrest import create_app, Middlewares

# Cria a aplicação
app = create_app()

# Configurações de JWT
JWT_SECRET = "sua_chave_secreta_muito_segura_2024"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 3600  # 1 hora

# Simula uma base de dados de usuários
users_db = {
    "admin@email.com": {
        "id": 1,
        "name": "Administrador",
        "email": "admin@email.com",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin"
    },
    "user@email.com": {
        "id": 2,
        "name": "Usuário Comum",
        "email": "user@email.com",
        "password_hash": hashlib.sha256("user123".encode()).hexdigest(),
        "role": "user"
    }
}

# Middlewares globais
app.use(Middlewares.cors())
app.use(Middlewares.logger("dev"))
app.use(Middlewares.json_parser())
app.use(Middlewares.security_headers())

def generate_token(user_data):
    """Gera um token JWT"""
    payload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "role": user_data["role"],
        "exp": datetime.now() + timedelta(seconds=JWT_EXPIRATION),
        "iat": datetime.now()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    """Verifica um token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def auth_middleware(req, res):
    """Middleware de autenticação personalizado"""
    # Rotas públicas que não precisam de autenticação
    public_routes = ["/", "/auth/login", "/auth/register", "/health"]
    
    if req.path in public_routes:
        return True  # Continua a execução
    
    # Verifica o token de autorização
    auth_header = req.get_header("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        res.status(401).json({
            "error": "Unauthorized",
            "message": "Token de autorização é obrigatório"
        })
        return False
    
    token = auth_header[7:]  # Remove "Bearer "
    payload = verify_token(token)
    
    if not payload:
        res.status(401).json({
            "error": "Unauthorized",
            "message": "Token inválido ou expirado"
        })
        return False
    
    # Adiciona dados do usuário à requisição
    req.user = payload
    return True

def admin_middleware(req, res):
    """Middleware para verificar se o usuário é admin"""
    if not hasattr(req, 'user'):
        res.status(401).json({
            "error": "Unauthorized",
            "message": "Autenticação necessária"
        })
        return False
    
    if req.user.get("role") != "admin":
        res.status(403).json({
            "error": "Forbidden",
            "message": "Acesso negado. Apenas administradores podem acessar este recurso."
        })
        return False
    
    return True

# Adiciona middleware de autenticação
app.use(auth_middleware)

# Rota principal
@app.get('/')
def home(req, res):
    res.json({
        "message": "🔐 API de Autenticação - PYREST-FRAMEWORK",
        "version": "1.0.0",
        "endpoints": {
            "login": "/auth/login",
            "register": "/auth/register",
            "profile": "/auth/profile",
            "users": "/api/users (admin only)",
            "health": "/health"
        }
    })

# Health check
@app.get('/health')
def health_check(req, res):
    res.json({
        "status": "OK",
        "service": "PyRest Auth API",
        "timestamp": datetime.now().isoformat()
    })

# Registro de usuário
@app.post('/auth/register')
def register(req, res):
    data = req.json_data
    
    if not data:
        res.status(400).json({
            "error": "Missing data",
            "message": "Dados de registro são obrigatórios"
        })
        return
    
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if field not in data:
            res.status(400).json({
                "error": "Missing field",
                "message": f"Campo '{field}' é obrigatório"
            })
            return
    
    email = data['email']
    
    # Verifica se o usuário já existe
    if email in users_db:
        res.status(409).json({
            "error": "User already exists",
            "message": "Este email já está registrado"
        })
        return
    
    # Cria novo usuário
    new_user = {
        "id": max(u["id"] for u in users_db.values()) + 1,
        "name": data['name'],
        "email": email,
        "password_hash": hashlib.sha256(data['password'].encode()).hexdigest(),
        "role": "user"  # Por padrão, usuários comuns
    }
    
    users_db[email] = new_user
    
    # Gera token
    token = generate_token(new_user)
    
    res.status(201).json({
        "message": "Usuário registrado com sucesso",
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "email": new_user["email"],
            "role": new_user["role"]
        },
        "token": token,
        "expires_in": JWT_EXPIRATION
    })

# Login
@app.post('/auth/login')
def login(req, res):
    data = req.json_data
    
    if not data:
        res.status(400).json({
            "error": "Missing data",
            "message": "Email e senha são obrigatórios"
        })
        return
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        res.status(400).json({
            "error": "Missing credentials",
            "message": "Email e senha são obrigatórios"
        })
        return
    
    # Verifica se o usuário existe
    user = users_db.get(email)
    if not user:
        res.status(401).json({
            "error": "Invalid credentials",
            "message": "Email ou senha incorretos"
        })
        return
    
    # Verifica a senha
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user["password_hash"] != password_hash:
        res.status(401).json({
            "error": "Invalid credentials",
            "message": "Email ou senha incorretos"
        })
        return
    
    # Gera token
    token = generate_token(user)
    
    res.json({
        "message": "Login realizado com sucesso",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        },
        "token": token,
        "expires_in": JWT_EXPIRATION
    })

# Perfil do usuário (rota protegida)
@app.get('/auth/profile')
def get_profile(req, res):
    # req.user contém os dados do token JWT
    user_id = req.user["user_id"]
    
    # Busca dados completos do usuário
    user = next((u for u in users_db.values() if u["id"] == user_id), None)
    
    if not user:
        res.status(404).json({
            "error": "User not found",
            "message": "Usuário não encontrado"
        })
        return
    
    res.json({
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    })

# Atualizar perfil
@app.put('/auth/profile')
def update_profile(req, res):
    data = req.json_data
    user_id = req.user["user_id"]
    
    if not data:
        res.status(400).json({
            "error": "Missing data",
            "message": "Dados para atualização são obrigatórios"
        })
        return
    
    # Encontra o usuário
    user = next((u for u in users_db.values() if u["id"] == user_id), None)
    
    if not user:
        res.status(404).json({
            "error": "User not found",
            "message": "Usuário não encontrado"
        })
        return
    
    # Atualiza campos permitidos
    allowed_fields = ['name']
    for field in allowed_fields:
        if field in data:
            user[field] = data[field]
    
    # Se forneceu nova senha, atualiza
    if 'password' in data:
        user["password_hash"] = hashlib.sha256(data['password'].encode()).hexdigest()
    
    res.json({
        "message": "Perfil atualizado com sucesso",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    })

# Lista todos os usuários (apenas admin)
@app.get('/api/users')
def get_users(req, res):
    # Verifica se é admin
    if not admin_middleware(req, res):
        return
    
    users_list = []
    for user in users_db.values():
        users_list.append({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        })
    
    res.json({
        "users": users_list,
        "total": len(users_list)
    })

# Verificar token
@app.post('/auth/verify')
def verify_token_route(req, res):
    data = req.json_data
    
    if not data or 'token' not in data:
        res.status(400).json({
            "error": "Missing token",
            "message": "Token é obrigatório"
        })
        return
    
    payload = verify_token(data['token'])
    
    if payload:
        res.json({
            "valid": True,
            "user": {
                "user_id": payload["user_id"],
                "email": payload["email"],
                "role": payload["role"]
            },
            "expires_at": datetime.fromtimestamp(payload["exp"]).isoformat()
        })
    else:
        res.status(401).json({
            "valid": False,
            "message": "Token inválido ou expirado"
        })

# Refresh token
@app.post('/auth/refresh')
def refresh_token(req, res):
    data = req.json_data
    
    if not data or 'token' not in data:
        res.status(400).json({
            "error": "Missing token",
            "message": "Token é obrigatório"
        })
        return
    
    # Verifica o token atual
    payload = verify_token(data['token'])
    
    if not payload:
        res.status(401).json({
            "error": "Invalid token",
            "message": "Token inválido ou expirado"
        })
        return
    
    # Busca dados do usuário
    user = next((u for u in users_db.values() if u["id"] == payload["user_id"]), None)
    
    if not user:
        res.status(404).json({
            "error": "User not found",
            "message": "Usuário não encontrado"
        })
        return
    
    # Gera novo token
    new_token = generate_token(user)
    
    res.json({
        "message": "Token renovado com sucesso",
        "token": new_token,
        "expires_in": JWT_EXPIRATION
    })

if __name__ == '__main__':
    print("🔐 Iniciando API de Autenticação do PYREST-FRAMEWORK...")
    print("📍 Endpoints disponíveis:")
    print("   • GET  / - Página inicial")
    print("   • POST /auth/register - Registro de usuário")
    print("   • POST /auth/login - Login")
    print("   • GET  /auth/profile - Perfil do usuário (protegido)")
    print("   • PUT  /auth/profile - Atualizar perfil (protegido)")
    print("   • POST /auth/verify - Verificar token")
    print("   • POST /auth/refresh - Renovar token")
    print("   • GET  /api/users - Lista usuários (apenas admin)")
    print("   • GET  /health - Health check")
    print("\n🔑 Usuários de teste:")
    print("   • admin@email.com / admin123 (admin)")
    print("   • user@email.com / user123 (user)")
    print("\n🔥 Servidor rodando em http://localhost:3000")
    
    app.listen(port=3000, debug=True)
