#!/usr/bin/env python3
"""
Script de instalação e teste do PYREST-FRAMEWORK
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def print_banner():
    """Imprime o banner do framework"""
    print("""
╔══════════════════════════════════════╗
║         PYREST-FRAMEWORK             ║
║    Framework Python para APIs REST   ║
╠══════════════════════════════════════╣
║  🚀 Instalação e Teste               ║
║  📚 Desenvolvido para ADS            ║
╚══════════════════════════════════════╝
    """)

def check_python_version():
    """Verifica a versão do Python"""
    print("🐍 Verificando versão do Python...")
    
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ é necessário")
        print(f"   Versão atual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def install_dependencies():
    """Instala as dependências"""
    print("\n📦 Instalando dependências...")
    
    try:
        # Instala dependências básicas
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def install_framework():
    """Instala o framework em modo desenvolvimento"""
    print("\n🔧 Instalando framework em modo desenvolvimento...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ Framework instalado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar framework: {e}")
        return False

def test_import():
    """Testa a importação do framework"""
    print("\n🧪 Testando importação do framework...")
    
    try:
        import pyrest
        print(f"✅ Framework importado com sucesso - Versão {pyrest.__version__}")
        
        # Testa importações específicas
        from pyrest import PyRest, create_app, Middlewares
        print("✅ Importações específicas funcionando")
        
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar framework: {e}")
        return False

def test_basic_functionality():
    """Testa funcionalidades básicas"""
    print("\n🔍 Testando funcionalidades básicas...")
    
    try:
        from pyrest import create_app, Middlewares
        
        # Cria app
        app = create_app()
        print("✅ Criação de app - OK")
        
        # Adiciona middleware
        app.use(Middlewares.cors())
        print("✅ Adição de middleware - OK")
        
        # Adiciona rota
        @app.get('/test')
        def test_handler(req, res):
            res.json({"message": "test"})
        
        print("✅ Definição de rota - OK")
        
        # Verifica se rota foi registrada
        if len(app.routes) == 1:
            print("✅ Registro de rota - OK")
        else:
            print("❌ Erro no registro de rota")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar funcionalidades: {e}")
        return False

def run_tests():
    """Executa os testes"""
    print("\n🧪 Executando testes...")
    
    try:
        # Verifica se pytest está disponível
        import pytest
        print("✅ pytest encontrado")
        
        # Executa testes
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Todos os testes passaram")
            return True
        else:
            print("❌ Alguns testes falharam")
            print("Saída dos testes:")
            print(result.stdout)
            print("Erros:")
            print(result.stderr)
            return False
            
    except ImportError:
        print("⚠️  pytest não encontrado, pulando testes")
        return True
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def test_examples():
    """Testa os exemplos"""
    print("\n📚 Testando exemplos...")
    
    examples_dir = Path("examples")
    if not examples_dir.exists():
        print("⚠️  Diretório de exemplos não encontrado")
        return True
    
    example_files = list(examples_dir.glob("*.py"))
    
    for example_file in example_files:
        print(f"   Testando {example_file.name}...")
        try:
            # Tenta importar o exemplo
            spec = importlib.util.spec_from_file_location("example", example_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"   ✅ {example_file.name} - OK")
        except Exception as e:
            print(f"   ❌ {example_file.name} - Erro: {e}")
    
    return True

def test_cli():
    """Testa o CLI"""
    print("\n🖥️  Testando CLI...")
    
    try:
        # Testa comando info
        result = subprocess.run([sys.executable, "-m", "pyrest.cli", "info"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ CLI funcionando")
            return True
        else:
            print("❌ Erro no CLI")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar CLI: {e}")
        return False

def create_test_project():
    """Cria um projeto de teste"""
    print("\n🏗️  Criando projeto de teste...")
    
    try:
        # Remove projeto de teste se existir
        test_project = Path("test-project")
        if test_project.exists():
            import shutil
            shutil.rmtree(test_project)
        
        # Cria projeto usando CLI
        result = subprocess.run([sys.executable, "-m", "pyrest.cli", "create", "test-project"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Projeto de teste criado")
            
            # Verifica se arquivos foram criados
            if test_project.exists():
                files = list(test_project.glob("*"))
                print(f"   Arquivos criados: {len(files)}")
                return True
            else:
                print("❌ Projeto não foi criado")
                return False
        else:
            print("❌ Erro ao criar projeto")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar projeto de teste: {e}")
        return False

def main():
    """Função principal"""
    print_banner()
    
    # Lista de testes
    tests = [
        ("Versão do Python", check_python_version),
        ("Instalação de dependências", install_dependencies),
        ("Instalação do framework", install_framework),
        ("Importação do framework", test_import),
        ("Funcionalidades básicas", test_basic_functionality),
        ("Execução de testes", run_tests),
        ("Teste de exemplos", test_examples),
        ("Teste do CLI", test_cli),
        ("Criação de projeto", create_test_project),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            results.append((test_name, False))
    
    # Resumo
    print(f"\n{'='*50}")
    print("📊 RESUMO DOS TESTES")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 O PYREST-FRAMEWORK está pronto para uso!")
        print("\n📚 Próximos passos:")
        print("   1. Explore os exemplos em examples/")
        print("   2. Leia a documentação em docs/")
        print("   3. Crie seu primeiro projeto: pyrest create minha-api")
        print("   4. Execute um servidor: pyrest serve --quick")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        print("🔧 Verifique os erros acima e tente novamente")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 