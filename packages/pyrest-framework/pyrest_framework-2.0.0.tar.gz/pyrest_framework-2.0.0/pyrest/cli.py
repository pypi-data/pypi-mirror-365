"""
CLI (Command Line Interface) para o PYREST-FRAMEWORK
"""

import argparse
import sys
import os
from pathlib import Path
from .utils import create_app, quick_start, generate_project_template

def create_project(args):
    """Cria um novo projeto PyRest"""
    project_name = args.name
    output_dir = args.output or "."
    
    try:
        generate_project_template(project_name, output_dir)
        print(f"\n✅ Projeto '{project_name}' criado com sucesso!")
        print(f"📁 Localização: {os.path.join(output_dir, project_name)}")
        print(f"\n🚀 Para começar:")
        print(f"   cd {project_name}")
        print(f"   python app.py")
    except Exception as e:
        print(f"❌ Erro ao criar projeto: {e}")
        sys.exit(1)

def serve_app(args):
    """Inicia um servidor PyRest"""
    port = args.port or 3000
    host = args.host or "localhost"
    debug = args.debug
    
    try:
        if args.quick:
            # Modo quick start
            quick_start(port=port, host=host, debug=debug)
        else:
            # Modo normal - carrega app.py
            app_file = args.app or "app.py"
            
            if not os.path.exists(app_file):
                print(f"❌ Arquivo '{app_file}' não encontrado")
                print("💡 Use --quick para iniciar um servidor de exemplo")
                sys.exit(1)
            
            # Carrega o app dinamicamente
            import importlib.util
            spec = importlib.util.spec_from_file_location("app", app_file)
            app_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(app_module)
            
            # Se o módulo tem uma variável 'app', usa ela
            if hasattr(app_module, 'app'):
                app = app_module.app
                app.listen(port=port, host=host, debug=debug)
            else:
                print(f"❌ Variável 'app' não encontrada em '{app_file}'")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

def show_info(args):
    """Mostra informações sobre o framework"""
    from . import __version__, __author__, __description__
    
    print("🚀 PYREST-FRAMEWORK")
    print("=" * 50)
    print(f"Versão: {__version__}")
    print(f"Autor: {__author__}")
    print(f"Descrição: {__description__}")
    print("\n📚 Comandos disponíveis:")
    print("   pyrest create <nome> - Cria novo projeto")
    print("   pyrest serve - Inicia servidor")
    print("   pyrest serve --quick - Inicia servidor de exemplo")
    print("   pyrest info - Mostra informações")
    print("\n🌐 Documentação: https://github.com/mamadusamadev/pyrest-framework")

def main():
    """Função principal do CLI"""
    parser = argparse.ArgumentParser(
        description="PYREST-FRAMEWORK - Framework Python para APIs REST",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  pyrest create minha-api
  pyrest serve --quick
  pyrest serve --port 8080 --debug
  pyrest serve app.py --host 0.0.0.0
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando create
    create_parser = subparsers.add_parser('create', help='Cria novo projeto')
    create_parser.add_argument('name', help='Nome do projeto')
    create_parser.add_argument('-o', '--output', help='Diretório de saída (padrão: atual)')
    create_parser.set_defaults(func=create_project)
    
    # Comando serve
    serve_parser = subparsers.add_parser('serve', help='Inicia servidor')
    serve_parser.add_argument('app', nargs='?', help='Arquivo da aplicação (padrão: app.py)')
    serve_parser.add_argument('-p', '--port', type=int, help='Porta (padrão: 3000)')
    serve_parser.add_argument('-H', '--host', help='Host (padrão: localhost)')
    serve_parser.add_argument('-d', '--debug', action='store_true', help='Modo debug')
    serve_parser.add_argument('-q', '--quick', action='store_true', help='Inicia servidor de exemplo')
    serve_parser.set_defaults(func=serve_app)
    
    # Comando info
    info_parser = subparsers.add_parser('info', help='Mostra informações do framework')
    info_parser.set_defaults(func=show_info)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)

if __name__ == '__main__':
    main() 