# Guia de Publicação no PyPI - PYREST-FRAMEWORK

Este guia explica como publicar o PYREST-FRAMEWORK no Python Package Index (PyPI).

## 📋 Pré-requisitos

### 1. Conta no PyPI
- Crie uma conta em [PyPI](https://pypi.org/account/register/)
- Crie uma conta em [TestPyPI](https://test.pypi.org/account/register/)

### 2. Token de API
1. Vá para [PyPI Account Settings](https://pypi.org/manage/account/)
2. Clique em "Add API token"
3. Dê um nome ao token (ex: "pyrest-framework")
4. Copie o token gerado (formato: `pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### 3. Dependências Python
```bash
pip install build twine setuptools wheel
```

## 🔧 Configuração

### 1. Ficheiro .pypirc
Crie o ficheiro `~/.pypirc` (Linux/Mac) ou `%USERPROFILE%\.pypirc` (Windows):

```ini
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ IMPORTANTE:** Substitua `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` pelo seu token real.

## 🚀 Processo de Publicação

### Opção 1: Script Automatizado (Recomendado)

```bash
# Executa o script de build e publicação
python build_and_publish.py
```

O script irá:
1. Limpar builds anteriores
2. Verificar dependências
3. Construir o pacote
4. Verificar o pacote
5. Oferecer opções de upload

### Opção 2: Comandos Manuais

#### 1. Limpar builds anteriores
```bash
rm -rf build/ dist/ *.egg-info/
```

#### 2. Construir o pacote
```bash
# Método moderno (recomendado)
python -m build

# Ou método tradicional
python setup.py sdist bdist_wheel
```

#### 3. Verificar o pacote
```bash
twine check dist/*
```

#### 4. Upload de teste (TestPyPI)
```bash
twine upload --repository testpypi dist/*
```

#### 5. Testar instalação do TestPyPI
```bash
pip install --index-url https://test.pypi.org/simple/ pyrest-framework
```

#### 6. Upload para PyPI oficial
```bash
twine upload dist/*
```

## 📦 Estrutura do Pacote

O pacote inclui:
- `pyrest/` - Código principal do framework
- `docs/` - Documentação
- `examples/` - Exemplos de uso
- `tests/` - Testes unitários
- `README.md` - Documentação principal
- `LICENSE` - Licença MIT

## 🔍 Verificações Antes da Publicação

### 1. Testes
```bash
pytest
```

### 2. Verificação de qualidade
```bash
# Formatação
black pyrest/ tests/ examples/

# Linting
flake8 pyrest/ tests/ examples/

# Type checking
mypy pyrest/
```

### 3. Verificação do pacote
```bash
# Verifica se o pacote pode ser instalado
pip install dist/*.whl

# Testa importação
python -c "import pyrest; print(pyrest.__version__)"
```

## 🎯 Versões

### Atualizar versão
1. Edite `pyrest/__init__.py`:
   ```python
   __version__ = "1.0.1"  # Incrementar versão
   ```

2. Edite `pyproject.toml`:
   ```toml
   version = "1.0.1"
   ```

3. Edite `setup.py`:
   ```python
   version="1.0.1",
   ```

### Convenções de versão
- `1.0.0` - Primeira versão estável
- `1.0.1` - Correções de bugs
- `1.1.0` - Novas funcionalidades
- `2.0.0` - Mudanças incompatíveis

## 🚨 Problemas Comuns

### Erro: "File already exists"
```bash
# Limpe builds anteriores
rm -rf build/ dist/ *.egg-info/
```

### Erro: "Invalid distribution"
```bash
# Verifique o pacote
twine check dist/*
```

### Erro: "Authentication failed"
- Verifique se o token está correto no `.pypirc`
- Certifique-se de que o token tem permissões de upload

### Erro: "Package name already exists"
- Verifique se o nome `pyrest-framework` está disponível
- Se não estiver, escolha outro nome no `pyproject.toml`

## 📚 Recursos Úteis

- [PyPI Documentation](https://packaging.python.org/tutorials/packaging-projects/)
- [TestPyPI](https://test.pypi.org/)
- [Python Packaging Authority](https://www.pypa.io/)

## 🎉 Após a Publicação

1. Verifique se o pacote aparece em [PyPI](https://pypi.org/project/pyrest-framework/)
2. Teste a instalação:
   ```bash
   pip install pyrest-framework
   ```
3. Atualize a documentação do GitHub
4. Crie uma release no GitHub

## 🔄 Atualizações Futuras

Para atualizar o pacote:
1. Incremente a versão
2. Execute `python build_and_publish.py`
3. Escolha a opção de upload para PyPI

---

**Happy publishing! 🚀** 