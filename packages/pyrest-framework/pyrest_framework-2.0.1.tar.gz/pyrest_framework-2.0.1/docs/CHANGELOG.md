# Changelog - PYREST-FRAMEWORK

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2024-01-01

### Adicionado
- 🎉 **Lançamento inicial do PYREST-FRAMEWORK**
- **Classe PyRestFramework**: Framework principal com suporte a rotas HTTP
- **Sistema de Roteamento**: Suporte a GET, POST, PUT, DELETE, PATCH, OPTIONS
- **Parâmetros de Rota**: Suporte a parâmetros dinâmicos (`:id`)
- **Sistema de Middlewares**: Middlewares globais e por rota
- **Classe Request**: Objeto de requisição com parsing automático
- **Classe Response**: Objeto de resposta com múltiplos formatos
- **Classe Route**: Gerenciamento de rotas com regex
- **Handlers de Erro**: Tratamento personalizado de erros HTTP
- **Query Parameters**: Suporte a parâmetros de query string
- **JSON Parsing**: Parsing automático de JSON
- **CORS**: Middleware CORS incluído
- **Logging**: Middleware de logging com múltiplos formatos
- **Security Headers**: Headers de segurança básicos
- **Static Files**: Middleware para servir arquivos estáticos
- **Rate Limiting**: Middleware básico de rate limiting
- **Authentication**: Middleware de autenticação básica
- **CLI**: Interface de linha de comando
- **Utilitários**: Funções auxiliares e helpers
- **Templates**: Geração de templates de projeto
- **Validação**: Validação básica de dados JSON
- **Benchmark**: Ferramenta de benchmark
- **Documentação**: Documentação completa da API
- **Exemplos**: Exemplos práticos de uso
- **Testes**: Suite de testes unitários

### Características Técnicas
- **Zero Dependências**: Apenas Python padrão
- **Compatibilidade**: Python 3.7+
- **Sintaxe Familiar**: Inspirado no Express.js
- **Performance**: Servidor HTTP nativo
- **Flexibilidade**: Middlewares customizáveis
- **Extensibilidade**: Fácil de estender

### Exemplos Incluídos
- **API Básica**: Exemplo simples de CRUD
- **Autenticação**: Sistema completo com JWT
- **CRUD Avançado**: Com validação, paginação e filtros

### Documentação
- **README**: Documentação principal
- **API Reference**: Referência completa da API
- **Changelog**: Histórico de versões
- **Exemplos**: Código de exemplo comentado

### Ferramentas de Desenvolvimento
- **CLI**: Comandos para criar projetos e iniciar servidores
- **Testes**: Suite de testes com pytest
- **Linting**: Configuração para flake8 e black
- **Type Checking**: Configuração para mypy
- **Coverage**: Relatórios de cobertura de código

---

## [0.9.0] - 2023-12-15

### Adicionado
- Versão beta inicial
- Funcionalidades básicas de roteamento
- Sistema de middlewares simples
- Parsing básico de JSON

### Mudanças
- Refatoração da arquitetura principal
- Melhorias na performance
- Correções de bugs menores

---

## [0.8.0] - 2023-12-01

### Adicionado
- Primeira versão alpha
- Conceito inicial do framework
- Roteamento básico
- Servidor HTTP simples

---

## Notas de Versão

### Versão 1.0.0
Esta é a primeira versão estável do PYREST-FRAMEWORK. O framework está pronto para uso em produção para projetos pequenos e médios.

**Compatibilidade**: Python 3.7+

**Instalação**:
```bash
pip install pyrest-framework
```

**Uso Básico**:
```python
from pyrest import create_app

app = create_app()

@app.get('/')
def home(req, res):
    res.json({"message": "Hello PyRest!"})

app.listen(3000)
```

### Próximas Versões

#### [1.1.0] - Planejado
- Suporte a WebSockets
- Middleware de compressão (gzip)
- Validação de dados mais robusta
- Suporte a upload de arquivos
- Cache middleware
- Rate limiting mais avançado

#### [1.2.0] - Planejado
- Suporte a templates HTML
- Middleware de sessão
- Integração com bases de dados
- ORM básico
- Migrations

#### [2.0.0] - Planejado
- Suporte a async/await
- Performance melhorada
- Arquitetura modular
- Plugins system
- API mais robusta

---

## Como Contribuir

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Relatórios de Bugs

Se você encontrar um bug, por favor abra uma issue no GitHub com:
- Descrição detalhada do bug
- Passos para reproduzir
- Comportamento esperado vs atual
- Informações do sistema (OS, Python version, etc.)

## Sugestões de Features

Para sugerir novas features:
1. Verifique se já não existe uma issue similar
2. Abra uma nova issue com a descrição da feature
3. Discuta a implementação com a comunidade
4. Implemente e envie um Pull Request

---

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](../LICENSE) para detalhes.

## Agradecimentos

- Inspirado no Express.js
- Comunidade Python
- Contribuidores e testadores
- Projetos open source que serviram como referência
