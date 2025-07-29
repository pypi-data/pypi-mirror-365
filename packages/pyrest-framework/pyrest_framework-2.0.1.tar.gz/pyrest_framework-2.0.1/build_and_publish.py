#!/usr/bin/env python3
"""
Script para build e publicação do PYREST-FRAMEWORK no PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description, interactive=False):
    """Executa um comando e mostra o resultado"""
    print(f"\n🔧 {description}...")
    print(f"Comando: {command}")
    
    try:
        if interactive:
            # Para comandos interativos (como twine upload)
            result = subprocess.run(command, shell=True, check=True)
        else:
            # Para comandos não interativos
            result = subprocess.run(command, shell=True, check=True, 
                                  capture_output=True, text=True)
            if result.stdout:
                print(f"Saída: {result.stdout}")
        
        print(f"✅ {description} concluído com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro em {description}:")
        if not interactive and e.stderr:
            print(f"Erro: {e.stderr}")
        return False

def clean_build():
    """Limpa diretórios de build anteriores"""
    print("\n🧹 Limpando builds anteriores...")
    
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   Removido: {path}")
            elif path.is_file():
                path.unlink()
                print(f"   Removido: {path}")

def check_dependencies():
    """Verifica se as dependências necessárias estão instaladas"""
    print("\n📦 Verificando dependências...")
    
    required_packages = ['build', 'twine', 'setuptools', 'wheel']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} não encontrado")
            print(f"   💡 Instale com: pip install {package}")
            return False
    
    return True

def build_package():
    """Constrói o pacote"""
    print("\n🏗️ Construindo pacote...")
    
    # Usa pyproject.toml (método moderno)
    if os.path.exists('pyproject.toml'):
        return run_command('python -m build', 'Build com pyproject.toml')
    else:
        return run_command('python setup.py sdist bdist_wheel', 'Build com setup.py')

def check_package():
    """Verifica o pacote construído"""
    print("\n🔍 Verificando pacote...")
    
    # Verifica se os arquivos foram criados
    dist_files = list(Path('dist').glob('*'))
    
    if not dist_files:
        print("❌ Nenhum arquivo encontrado em dist/")
        return False
    
    print(f"✅ Arquivos criados:")
    for file in dist_files:
        print(f"   {file}")
    
    # Verifica com twine
    return run_command('twine check dist/*', 'Verificação com twine')

def test_upload():
    """Faz upload de teste para TestPyPI"""
    print("\n🧪 Fazendo upload de teste para TestPyPI...")
    
    print("\n💡 O comando vai pedir o teu token TestPyPI.")
    print("💡 Cola o token quando solicitado (não será visível por segurança).")
    
    return run_command('twine upload --repository testpypi dist/*', 'Upload para TestPyPI', interactive=True)

def upload_to_pypi():
    """Faz upload para PyPI oficial"""
    print("\n🚀 Fazendo upload para PyPI...")
    
    # Confirmação do usuário
    response = input("\n⚠️ Tem certeza que quer fazer upload para PyPI oficial? (y/N): ")
    if response.lower() != 'y':
        print("❌ Upload cancelado")
        return False
    
    print("\n💡 O comando vai pedir o teu token PyPI.")
    print("💡 Cola o token quando solicitado (não será visível por segurança).")
    
    return run_command('twine upload dist/*', 'Upload para PyPI', interactive=True)

def main():
    """Função principal"""
    print("🚀 PYREST-FRAMEWORK - Build e Publicação")
    print("=" * 50)
    
    # Verifica se estamos no diretório correto
    if not os.path.exists('pyproject.toml') and not os.path.exists('setup.py'):
        print("❌ Não encontrei pyproject.toml ou setup.py")
        print("💡 Execute este script no diretório raiz do projeto")
        sys.exit(1)
    
    # Limpa builds anteriores
    clean_build()
    
    # Verifica dependências
    if not check_dependencies():
        print("\n❌ Dependências em falta. Instale-as primeiro:")
        print("pip install build twine setuptools wheel")
        sys.exit(1)
    
    # Constrói o pacote
    if not build_package():
        print("\n❌ Erro ao construir o pacote")
        sys.exit(1)
    
    # Verifica o pacote
    if not check_package():
        print("\n❌ Erro na verificação do pacote")
        sys.exit(1)
    
    print("\n✅ Pacote construído com sucesso!")
    
    # Pergunta o que fazer
    print("\n📋 Opções disponíveis:")
    print("1. Upload de teste para TestPyPI")
    print("2. Upload para PyPI oficial")
    print("3. Apenas construir (sem upload)")
    
    choice = input("\nEscolha uma opção (1-3): ")
    
    if choice == '1':
        test_upload()
    elif choice == '2':
        upload_to_pypi()
    elif choice == '3':
        print("\n✅ Build concluído! Arquivos em dist/")
    else:
        print("\n❌ Opção inválida")

if __name__ == '__main__':
    main() 