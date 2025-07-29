"""
Sistema de Banco de Dados para PYREST-FRAMEWORK
Integração completa com Prisma e múltiplos bancos de dados
"""

import os
import subprocess
import sys
from typing import Optional, Dict, Any
from pathlib import Path

class DatabaseConfig:
    """Configuração de banco de dados"""
    
    def __init__(self, database_url: str = None, provider: str = "postgresql"):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        self.provider = provider
        self.schema_path = "prisma/schema.prisma"
        
    def get_database_url(self) -> str:
        """Retorna a URL do banco de dados"""
        if not self.database_url:
            raise ValueError("DATABASE_URL não configurada")
        return self.database_url

class PrismaSetup:
    """Configuração e setup do Prisma"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.prisma_dir = Path("prisma")
        self.schema_file = self.prisma_dir / "schema.prisma"
    
    def create_prisma_directory(self):
        """Cria o diretório prisma se não existir"""
        self.prisma_dir.mkdir(exist_ok=True)
        print(f"✅ Diretório prisma criado: {self.prisma_dir}")
    
    def create_schema_file(self, models: Dict[str, Any] = None):
        """Cria o arquivo schema.prisma"""
        if not models:
            models = self._get_default_models()
        
        schema_content = self._generate_schema_content(models)
        
        with open(self.schema_file, 'w', encoding='utf-8') as f:
            f.write(schema_content)
        
        print(f"✅ Schema Prisma criado: {self.schema_file}")
    
    def _get_default_models(self) -> Dict[str, Any]:
        """Retorna modelos padrão"""
        return {
            "User": {
                "fields": [
                    {"name": "id", "type": "String", "attributes": ["@id", "@default(cuid)"]},
                    {"name": "name", "type": "String"},
                    {"name": "email", "type": "String", "attributes": ["@unique"]},
                    {"name": "password", "type": "String"},
                    {"name": "role", "type": "String", "default": "user"},
                    {"name": "is_active", "type": "Boolean", "default": "true"},
                    {"name": "created_at", "type": "DateTime", "attributes": ["@default(now())"]},
                    {"name": "updated_at", "type": "DateTime", "attributes": ["@updatedAt"]}
                ]
            },
            "Product": {
                "fields": [
                    {"name": "id", "type": "String", "attributes": ["@id", "@default(cuid)"]},
                    {"name": "name", "type": "String"},
                    {"name": "description", "type": "String"},
                    {"name": "price", "type": "Float"},
                    {"name": "stock", "type": "Int", "default": "0"},
                    {"name": "category", "type": "String"},
                    {"name": "image_url", "type": "String", "optional": True},
                    {"name": "created_at", "type": "DateTime", "attributes": ["@default(now())"]},
                    {"name": "updated_at", "type": "DateTime", "attributes": ["@updatedAt"]}
                ]
            }
        }
    
    def _generate_schema_content(self, models: Dict[str, Any]) -> str:
        """Gera o conteúdo do schema.prisma"""
        content = f'''// This is your Prisma schema file,
// learn more about it in the docs: https://pris.ly/d/prisma-schema

generator client {{
  provider = "prisma-client-py"
}}

datasource db {{
  provider = "{self.config.provider}"
  url      = env("DATABASE_URL")
}}

'''
        
        for model_name, model_config in models.items():
            content += f"\nmodel {model_name} {{\n"
            
            for field in model_config["fields"]:
                field_line = f"  {field['name']} {field['type']}"
                
                if field.get("optional"):
                    field_line += "?"
                
                if "attributes" in field:
                    for attr in field["attributes"]:
                        field_line += f" {attr}"
                
                if "default" in field:
                    field_line += f" @default({field['default']})"
                
                content += field_line + "\n"
            
            content += "}\n"
        
        return content
    
    def install_prisma(self):
        """Instala o Prisma CLI"""
        try:
            # Verifica se o Prisma já está instalado
            result = subprocess.run(['prisma', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Prisma CLI já está instalado")
                return True
        except FileNotFoundError:
            pass
        
        print("📦 Instalando Prisma CLI...")
        
        try:
            # Instala via npm (se disponível)
            result = subprocess.run(['npm', 'install', '-g', 'prisma'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Prisma CLI instalado via npm")
                return True
        except FileNotFoundError:
            pass
        
        try:
            # Tenta instalar via yarn
            result = subprocess.run(['yarn', 'global', 'add', 'prisma'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Prisma CLI instalado via yarn")
                return True
        except FileNotFoundError:
            pass
        
        print("❌ Não foi possível instalar o Prisma CLI automaticamente")
        print("💡 Instale manualmente:")
        print("   npm install -g prisma")
        print("   ou")
        print("   yarn global add prisma")
        return False
    
    def generate_client(self):
        """Gera o cliente Prisma"""
        try:
            print("🔧 Gerando cliente Prisma...")
            result = subprocess.run(['prisma', 'generate'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Cliente Prisma gerado com sucesso")
                return True
            else:
                print(f"❌ Erro ao gerar cliente: {result.stderr}")
                return False
        except FileNotFoundError:
            print("❌ Prisma CLI não encontrado")
            return False
    
    def push_schema(self):
        """Faz push do schema para o banco"""
        try:
            print("🚀 Fazendo push do schema...")
            result = subprocess.run(['prisma', 'db', 'push'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Schema enviado para o banco com sucesso")
                return True
            else:
                print(f"❌ Erro ao fazer push: {result.stderr}")
                return False
        except FileNotFoundError:
            print("❌ Prisma CLI não encontrado")
            return False
    
    def migrate(self, name: str = "init"):
        """Cria uma migração"""
        try:
            print(f"🔄 Criando migração: {name}")
            result = subprocess.run(['prisma', 'migrate', 'dev', '--name', name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Migração criada com sucesso")
                return True
            else:
                print(f"❌ Erro na migração: {result.stderr}")
                return False
        except FileNotFoundError:
            print("❌ Prisma CLI não encontrado")
            return False

class DatabaseManager:
    """Gerenciador principal de banco de dados"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.setup = PrismaSetup(self.config)
        self.client = None
    
    def initialize(self, auto_setup: bool = True):
        """Inicializa o sistema de banco de dados"""
        print("🚀 Inicializando sistema de banco de dados...")
        
        if auto_setup:
            self.setup.create_prisma_directory()
            self.setup.create_schema_file()
            
            if self.setup.install_prisma():
                self.setup.generate_client()
        
        # Tenta conectar ao banco
        try:
            from prisma import Prisma
            self.client = Prisma()
            self.client.connect()
            print("✅ Conectado ao banco de dados")
            return True
        except ImportError:
            print("⚠️ Prisma não instalado. Execute: pip install prisma")
            return False
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do banco"""
        if self.client:
            self.client.disconnect()
            print("✅ Desconectado do banco de dados")
    
    def get_client(self):
        """Retorna o cliente Prisma"""
        return self.client

# Funções utilitárias
def setup_database(database_url: str = None, provider: str = "postgresql", 
                  auto_setup: bool = True) -> DatabaseManager:
    """Configura e inicializa o banco de dados"""
    config = DatabaseConfig(database_url, provider)
    manager = DatabaseManager(config)
    manager.initialize(auto_setup)
    return manager

def create_prisma_schema(models: Dict[str, Any] = None):
    """Cria um schema Prisma personalizado"""
    config = DatabaseConfig()
    setup = PrismaSetup(config)
    setup.create_prisma_directory()
    setup.create_schema_file(models)
    return setup

# Configurações de exemplo
POSTGRES_CONFIG = {
    "database_url": "postgresql://username:password@localhost:5432/database",
    "provider": "postgresql"
}

MYSQL_CONFIG = {
    "database_url": "mysql://username:password@localhost:3306/database",
    "provider": "mysql"
}

SQLITE_CONFIG = {
    "database_url": "file:./dev.db",
    "provider": "sqlite"
} 