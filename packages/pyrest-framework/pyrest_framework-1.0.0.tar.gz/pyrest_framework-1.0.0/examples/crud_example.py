"""
Exemplo completo de CRUD com PYREST-FRAMEWORK
Demonstra operações CRUD, validação, paginação e filtros
"""

import json
import re
from datetime import datetime
from pyrest import create_app, Middlewares

# Cria a aplicação
app = create_app()

# Middlewares globais
app.use(Middlewares.cors())
app.use(Middlewares.logger("dev"))
app.use(Middlewares.json_parser())
app.use(Middlewares.security_headers())

# Simula uma base de dados de produtos
products_db = [
    {
        "id": 1,
        "name": "Smartphone Galaxy S21",
        "description": "Smartphone Samsung Galaxy S21 128GB",
        "price": 2999.99,
        "category": "electronics",
        "stock": 15,
        "active": True,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
    },
    {
        "id": 2,
        "name": "Notebook Dell Inspiron",
        "description": "Notebook Dell Inspiron 15 polegadas 8GB RAM",
        "price": 4599.99,
        "category": "computers",
        "stock": 8,
        "active": True,
        "created_at": "2024-01-02T14:30:00Z",
        "updated_at": "2024-01-02T14:30:00Z"
    },
    {
        "id": 3,
        "name": "Fone de Ouvido Bluetooth",
        "description": "Fone de ouvido sem fio com cancelamento de ruído",
        "price": 299.99,
        "category": "accessories",
        "stock": 25,
        "active": True,
        "created_at": "2024-01-03T09:15:00Z",
        "updated_at": "2024-01-03T09:15:00Z"
    }
]

# Validação de dados
def validate_product(data, is_update=False):
    """Valida dados do produto"""
    errors = []
    
    if not is_update:
        # Campos obrigatórios para criação
        required_fields = ['name', 'price', 'category']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Campo '{field}' é obrigatório")
    
    # Validações específicas
    if 'name' in data:
        if len(data['name']) < 3:
            errors.append("Nome deve ter pelo menos 3 caracteres")
        if len(data['name']) > 100:
            errors.append("Nome deve ter no máximo 100 caracteres")
    
    if 'price' in data:
        try:
            price = float(data['price'])
            if price < 0:
                errors.append("Preço deve ser maior ou igual a zero")
        except (ValueError, TypeError):
            errors.append("Preço deve ser um número válido")
    
    if 'category' in data:
        valid_categories = ['electronics', 'computers', 'accessories', 'books', 'clothing']
        if data['category'] not in valid_categories:
            errors.append(f"Categoria deve ser uma das seguintes: {', '.join(valid_categories)}")
    
    if 'stock' in data:
        try:
            stock = int(data['stock'])
            if stock < 0:
                errors.append("Estoque deve ser maior ou igual a zero")
        except (ValueError, TypeError):
            errors.append("Estoque deve ser um número inteiro válido")
    
    return errors

def paginate_data(data, page=1, limit=10):
    """Aplica paginação aos dados"""
    try:
        page = max(1, int(page))
        limit = max(1, min(100, int(limit)))  # Máximo 100 itens por página
    except (ValueError, TypeError):
        page = 1
        limit = 10
    
    start_index = (page - 1) * limit
    end_index = start_index + limit
    
    paginated_data = data[start_index:end_index]
    
    return {
        "data": paginated_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(data),
            "pages": (len(data) + limit - 1) // limit,
            "has_next": end_index < len(data),
            "has_prev": page > 1
        }
    }

def filter_products(products, filters):
    """Aplica filtros aos produtos"""
    filtered = products.copy()
    
    # Filtro por nome (busca parcial)
    if 'name' in filters and filters['name']:
        search_term = filters['name'].lower()
        filtered = [p for p in filtered if search_term in p['name'].lower()]
    
    # Filtro por categoria
    if 'category' in filters and filters['category']:
        filtered = [p for p in filtered if p['category'] == filters['category']]
    
    # Filtro por preço mínimo
    if 'min_price' in filters and filters['min_price']:
        try:
            min_price = float(filters['min_price'])
            filtered = [p for p in filtered if p['price'] >= min_price]
        except (ValueError, TypeError):
            pass
    
    # Filtro por preço máximo
    if 'max_price' in filters and filters['max_price']:
        try:
            max_price = float(filters['max_price'])
            filtered = [p for p in filtered if p['price'] <= max_price]
        except (ValueError, TypeError):
            pass
    
    # Filtro por estoque
    if 'in_stock' in filters and filters['in_stock']:
        if filters['in_stock'].lower() == 'true':
            filtered = [p for p in filtered if p['stock'] > 0]
        elif filters['in_stock'].lower() == 'false':
            filtered = [p for p in filtered if p['stock'] == 0]
    
    # Filtro por status ativo
    if 'active' in filters and filters['active']:
        if filters['active'].lower() == 'true':
            filtered = [p for p in filtered if p['active']]
        elif filters['active'].lower() == 'false':
            filtered = [p for p in filtered if not p['active']]
    
    return filtered

def sort_products(products, sort_by='id', order='asc'):
    """Ordena produtos"""
    if not products:
        return products
    
    # Campos válidos para ordenação
    valid_fields = ['id', 'name', 'price', 'stock', 'created_at', 'updated_at']
    
    if sort_by not in valid_fields:
        sort_by = 'id'
    
    # Ordenação
    reverse = order.lower() == 'desc'
    
    try:
        if sort_by in ['price', 'stock', 'id']:
            # Ordenação numérica
            products.sort(key=lambda x: x[sort_by], reverse=reverse)
        else:
            # Ordenação alfabética
            products.sort(key=lambda x: x[sort_by].lower(), reverse=reverse)
    except (KeyError, TypeError):
        # Se houver erro, mantém ordem original
        pass
    
    return products

# Rota principal
@app.get('/')
def home(req, res):
    res.json({
        "message": "🛍️ API de Produtos - PYREST-FRAMEWORK",
        "version": "1.0.0",
        "endpoints": {
            "products": "/api/products",
            "product_by_id": "/api/products/:id",
            "categories": "/api/categories",
            "health": "/health"
        },
        "features": [
            "CRUD completo",
            "Validação de dados",
            "Paginação",
            "Filtros",
            "Ordenação"
        ]
    })

# Health check
@app.get('/health')
def health_check(req, res):
    res.json({
        "status": "OK",
        "service": "PyRest Products API",
        "timestamp": datetime.now().isoformat(),
        "total_products": len(products_db)
    })

# Lista categorias disponíveis
@app.get('/api/categories')
def get_categories(req, res):
    categories = ['electronics', 'computers', 'accessories', 'books', 'clothing']
    res.json({
        "categories": categories,
        "total": len(categories)
    })

# CRUD de Produtos

# GET - Lista produtos com filtros, paginação e ordenação
@app.get('/api/products')
def get_products(req, res):
    # Parâmetros de query
    page = req.get_query('page', '1')
    limit = req.get_query('limit', '10')
    sort_by = req.get_query('sort_by', 'id')
    order = req.get_query('order', 'asc')
    
    # Filtros
    filters = {
        'name': req.get_query('name'),
        'category': req.get_query('category'),
        'min_price': req.get_query('min_price'),
        'max_price': req.get_query('max_price'),
        'in_stock': req.get_query('in_stock'),
        'active': req.get_query('active')
    }
    
    # Remove filtros vazios
    filters = {k: v for k, v in filters.items() if v}
    
    # Aplica filtros
    filtered_products = filter_products(products_db, filters)
    
    # Aplica ordenação
    sorted_products = sort_products(filtered_products, sort_by, order)
    
    # Aplica paginação
    result = paginate_data(sorted_products, page, limit)
    
    res.json({
        "products": result["data"],
        "pagination": result["pagination"],
        "filters_applied": filters
    })

# GET - Busca produto por ID
@app.get('/api/products/:id')
def get_product_by_id(req, res):
    try:
        product_id = int(req.params['id'])
        product = next((p for p in products_db if p['id'] == product_id), None)
        
        if product:
            res.json(product)
        else:
            res.status(404).json({
                "error": "Product not found",
                "message": f"Produto com ID {product_id} não encontrado"
            })
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID",
            "message": "ID deve ser um número válido"
        })

# POST - Cria novo produto
@app.post('/api/products')
def create_product(req, res):
    data = req.json_data
    
    if not data:
        res.status(400).json({
            "error": "Missing data",
            "message": "Dados do produto são obrigatórios"
        })
        return
    
    # Valida dados
    errors = validate_product(data)
    if errors:
        res.status(400).json({
            "error": "Validation failed",
            "message": "Dados inválidos",
            "errors": errors
        })
        return
    
    # Verifica se já existe produto com mesmo nome
    if any(p['name'].lower() == data['name'].lower() for p in products_db):
        res.status(409).json({
            "error": "Product already exists",
            "message": "Já existe um produto com este nome"
        })
        return
    
    # Cria novo produto
    new_product = {
        "id": max(p['id'] for p in products_db) + 1,
        "name": data['name'],
        "description": data.get('description', ''),
        "price": float(data['price']),
        "category": data['category'],
        "stock": int(data.get('stock', 0)),
        "active": data.get('active', True),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    products_db.append(new_product)
    
    res.status(201).json({
        "message": "Produto criado com sucesso",
        "product": new_product
    })

# PUT - Atualiza produto completamente
@app.put('/api/products/:id')
def update_product(req, res):
    try:
        product_id = int(req.params['id'])
        data = req.json_data
        
        if not data:
            res.status(400).json({
                "error": "Missing data",
                "message": "Dados para atualização são obrigatórios"
            })
            return
        
        # Encontra o produto
        product_index = next((i for i, p in enumerate(products_db) if p['id'] == product_id), None)
        
        if product_index is None:
            res.status(404).json({
                "error": "Product not found",
                "message": f"Produto com ID {product_id} não encontrado"
            })
            return
        
        # Valida dados
        errors = validate_product(data, is_update=True)
        if errors:
            res.status(400).json({
                "error": "Validation failed",
                "message": "Dados inválidos",
                "errors": errors
            })
            return
        
        # Verifica se nome já existe em outro produto
        if 'name' in data:
            existing_product = next((p for p in products_db 
                                   if p['id'] != product_id and p['name'].lower() == data['name'].lower()), None)
            if existing_product:
                res.status(409).json({
                    "error": "Product already exists",
                    "message": "Já existe outro produto com este nome"
                })
                return
        
        # Atualiza o produto
        old_product = products_db[product_index]
        products_db[product_index].update({
            "name": data.get('name', old_product['name']),
            "description": data.get('description', old_product['description']),
            "price": float(data.get('price', old_product['price'])),
            "category": data.get('category', old_product['category']),
            "stock": int(data.get('stock', old_product['stock'])),
            "active": data.get('active', old_product['active']),
            "updated_at": datetime.now().isoformat()
        })
        
        res.json({
            "message": "Produto atualizado com sucesso",
            "product": products_db[product_index]
        })
        
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID",
            "message": "ID deve ser um número válido"
        })

# PATCH - Atualização parcial do produto
@app.patch('/api/products/:id')
def patch_product(req, res):
    try:
        product_id = int(req.params['id'])
        data = req.json_data
        
        if not data:
            res.status(400).json({
                "error": "Missing data",
                "message": "Dados para atualização são obrigatórios"
            })
            return
        
        # Encontra o produto
        product_index = next((i for i, p in enumerate(products_db) if p['id'] == product_id), None)
        
        if product_index is None:
            res.status(404).json({
                "error": "Product not found",
                "message": f"Produto com ID {product_id} não encontrado"
            })
            return
        
        # Valida apenas os campos fornecidos
        validation_data = {k: v for k, v in data.items() if k in ['name', 'price', 'category', 'stock']}
        if validation_data:
            errors = validate_product(validation_data, is_update=True)
            if errors:
                res.status(400).json({
                    "error": "Validation failed",
                    "message": "Dados inválidos",
                    "errors": errors
                })
                return
        
        # Verifica se nome já existe em outro produto
        if 'name' in data:
            existing_product = next((p for p in products_db 
                                   if p['id'] != product_id and p['name'].lower() == data['name'].lower()), None)
            if existing_product:
                res.status(409).json({
                    "error": "Product already exists",
                    "message": "Já existe outro produto com este nome"
                })
                return
        
        # Atualiza apenas os campos fornecidos
        for key, value in data.items():
            if key in ['name', 'description', 'price', 'category', 'stock', 'active']:
                if key in ['price']:
                    products_db[product_index][key] = float(value)
                elif key in ['stock']:
                    products_db[product_index][key] = int(value)
                elif key in ['active']:
                    products_db[product_index][key] = bool(value)
                else:
                    products_db[product_index][key] = value
        
        # Atualiza timestamp
        products_db[product_index]['updated_at'] = datetime.now().isoformat()
        
        res.json({
            "message": "Produto atualizado com sucesso",
            "product": products_db[product_index]
        })
        
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID",
            "message": "ID deve ser um número válido"
        })

# DELETE - Remove produto
@app.delete('/api/products/:id')
def delete_product(req, res):
    try:
        product_id = int(req.params['id'])
        
        # Encontra o produto
        product_index = next((i for i, p in enumerate(products_db) if p['id'] == product_id), None)
        
        if product_index is None:
            res.status(404).json({
                "error": "Product not found",
                "message": f"Produto com ID {product_id} não encontrado"
            })
            return
        
        # Remove o produto
        deleted_product = products_db.pop(product_index)
        
        res.json({
            "message": "Produto removido com sucesso",
            "product": deleted_product
        })
        
    except ValueError:
        res.status(400).json({
            "error": "Invalid ID",
            "message": "ID deve ser um número válido"
        })

# Estatísticas dos produtos
@app.get('/api/products/stats')
def get_products_stats(req, res):
    if not products_db:
        res.json({
            "total_products": 0,
            "total_value": 0,
            "categories_count": {},
            "average_price": 0,
            "low_stock_products": 0
        })
        return
    
    total_value = sum(p['price'] * p['stock'] for p in products_db)
    average_price = sum(p['price'] for p in products_db) / len(products_db)
    
    # Conta produtos por categoria
    categories_count = {}
    for product in products_db:
        category = product['category']
        categories_count[category] = categories_count.get(category, 0) + 1
    
    # Produtos com estoque baixo (menos de 5)
    low_stock_products = len([p for p in products_db if p['stock'] < 5])
    
    res.json({
        "total_products": len(products_db),
        "total_value": round(total_value, 2),
        "categories_count": categories_count,
        "average_price": round(average_price, 2),
        "low_stock_products": low_stock_products
    })

if __name__ == '__main__':
    print("🛍️ Iniciando API de Produtos do PYREST-FRAMEWORK...")
    print("📍 Endpoints disponíveis:")
    print("   • GET  / - Página inicial")
    print("   • GET  /api/products - Lista produtos (com filtros e paginação)")
    print("   • GET  /api/products/:id - Busca produto por ID")
    print("   • POST /api/products - Cria novo produto")
    print("   • PUT  /api/products/:id - Atualiza produto")
    print("   • PATCH /api/products/:id - Atualização parcial")
    print("   • DELETE /api/products/:id - Remove produto")
    print("   • GET  /api/products/stats - Estatísticas")
    print("   • GET  /api/categories - Lista categorias")
    print("   • GET  /health - Health check")
    print("\n🔍 Exemplos de filtros:")
    print("   • /api/products?category=electronics")
    print("   • /api/products?min_price=100&max_price=1000")
    print("   • /api/products?name=phone&in_stock=true")
    print("   • /api/products?sort_by=price&order=desc")
    print("   • /api/products?page=1&limit=5")
    print("\n🔥 Servidor rodando em http://localhost:3000")
    
    app.listen(port=3000, debug=True)
