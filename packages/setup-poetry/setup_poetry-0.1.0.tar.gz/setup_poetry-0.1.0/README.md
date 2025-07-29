# Setup Poetry

## Instalar no Windows
```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

## Adicionar o poetry a variável de ambiente
```
rundll32 sysdm.cpl,EditEnvironmentVariables
```

Adicione o caminho do Poetry ao path
![image](assets/variavel-de-ambiente-poetry.png)

## Verifique se o Poetry está disponível
```
poetry --version
```


# Uso do Poetry

Este projeto utiliza o [Poetry](https://python-poetry.org/) para gerenciamento de dependências, ambientes virtuais e empacotamento de projetos Python.

---

## Iniciar o Poetry em um projeto existente
```
poetry init
```

## Criar um projeto no Poetry

Para criar um novo projeto com o Poetry:

```bash
poetry new <project_name>
```

> Esse comando cria um arquivo `pyproject.toml` com as configurações iniciais do projeto. Siga as instruções interativas para definir as dependências e metadados.

---

## Criar ambiente virtual

Configure para ele criar sempre local:
```
poetry config --list
```

Configurar o venv no ambiente local
```
poetry config virtualenvs.in-project true
```

Após inicializar o projeto:

```bash
poetry install
```

Ativar o ambiente virtual:

```bash
poetry shell
```

Sair do ambiente virtual
```
exit
```

---

## Instalar pacotes

Para adicionar uma dependência ao projeto:

```bash
poetry add nome-do-pacote
```

Para adicionar uma dependência somente para desenvolvimento (como linters, testadores, etc):

```bash
poetry add --group dev nome-do-pacote
```

---

## Boas práticas de adicionar pacotes nos grupos

Use os grupos de dependências para manter seu projeto organizado:

- **Dependências principais** (`[tool.poetry.dependencies]`): 
  - Bibliotecas que seu código precisa para funcionar.
  - Exemplo: `requests`, `pandas`, `sqlalchemy`.

```bash
poetry add pandas
```

- **Dependências de desenvolvimento** (`[tool.poetry.group.dev.dependencies]`): 
  - Ferramentas para testes, lint, formatação, etc.
  - Exemplo: `pytest`, `black`, `mypy`.

```bash
poetry add --group dev pytest
poetry add --group dev black
```

- **Outros grupos personalizados**:
  - Você pode criar grupos como `test`, `docs`, `ci` etc.

```bash
poetry add --group docs mkdocs
```

---

## Outros comandos úteis

- Atualizar as dependências:

```bash
poetry update
```

- Ver dependências do projeto:

```bash
poetry show
```

- Remover uma dependência:

```bash
poetry remove nome-do-pacote
```

- Executar comandos dentro do ambiente virtual:

```bash
poetry run python script.py
```

---

## 📁 Estrutura recomendada de projeto

```
.
├── pyproject.toml
├── poetry.lock
├── .venv/              
├── src/
│   └── nome_do_pacote/
│       └── __init__.py
├── tests/
│   └── test_*.py
```

---

Para mais informações, consulte a [documentação oficial do Poetry](https://python-poetry.org/docs/).
