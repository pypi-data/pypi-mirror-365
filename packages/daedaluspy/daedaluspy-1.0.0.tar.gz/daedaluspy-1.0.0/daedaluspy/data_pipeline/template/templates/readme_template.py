"""
Template para README.md - Documentação do pipeline
"""

README_TEMPLATE = '''# {project_name}

Pipeline de dados para coleta, processamento e salvamento de dados do sistema **{system_name}** (dados: **{dataname}**, tier: **{tier}**).

## Estrutura do Projeto

```
{project_name}/
├── __init__.py          # Exportações do módulo
├── main.py              # Função principal do pipeline
├── config.py            # Configurações e serviços
├── base.py              # Classes base
├── steps.py             # Steps de processamento
├── flowbuilder.py       # Orquestração do pipeline
├── README.md            # Este arquivo
├── requirements.txt     # Dependências
└── tests/              # Testes
    ├── __init__.py
    ├── test_steps.py
    ├── test_flowbuilder.py
    ├── test_main.py
    └── conftest.py
```

## Como Usar

### Execução Básica

```python
from {project_name} import main

# Executar pipeline
result = main()

if result["success"]:
    print("Pipeline executado com sucesso!")
else:
    print(f"Erro: {{result.get('error', 'Falha nos steps')}}")
```

### Execução com Data Específica

```python
from datetime import datetime
from {project_name} import main

# Executar para uma data específica
date_ref = datetime(2024, 1, 15)
result = main(date_reference=date_ref)
```

### Uso Avançado do FlowBuilder

```python
from datetime import datetime
from {project_name} import {project_class_name}FlowBuilder

# Criar builder
builder = {project_class_name}FlowBuilder()

# Executar pipeline passo a passo
builder.set_date_reference(datetime.now())\\
       .collect()\\
       .process()\\
       .save()

# Obter resultados detalhados
results = builder.get_results()
summary = builder.get_summary()

# Verificar cada step
for i, result in enumerate(results):
    print(f"Step {{i+1}}: {{result.success}} - {{result.message}}")
```

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Azure Storage
AZURE_STORAGE_ACCOUNT_NAME=your_account
AZURE_STORAGE_ACCOUNT_KEY=your_key

# Azure SQL Database
AZURE_SQL_SERVER=your_server.database.windows.net
AZURE_SQL_DATABASE=your_database
AZURE_SQL_USERNAME=your_username
AZURE_SQL_PASSWORD=your_password

# Sankhya API
SANKHYA_BASE_URL=https://api.sankhya.com.br
SANKHYA_APP_KEY=your_app_key
SANKHYA_USERNAME=your_username
SANKHYA_PASSWORD=your_password
```

### Configuração do Pipeline

O arquivo `config.py` contém todas as configurações:

- **Serviços**: Sankhya, Azure Storage, etc.
- **Entidades**: Destino dos dados processados
- **Spark**: Configurações do Spark Session

## Personalização

### Adicionando Novos Steps

1. Crie uma nova classe em `steps.py` herdando de `ProcessStep`:

```python
class MeuNovoStep(ProcessStep):
    def __init__(self):
        super().__init__("MeuNovoStep")
    
    def execute(self, data: pd.DataFrame) -> StepResult:
        # Sua lógica aqui
        return StepResult(success=True, data=data)
```

2. Adicione o step ao `FlowBuilder` em `flowbuilder.py`:

```python
def process(self):
    # Steps existentes...
    
    # Seu novo step
    novo_result = self.meu_novo_step.run(self.current_data)
    self.step_results.append(novo_result)
    
    return self
```

### Modificando a Coleta

Edite o método `collect()` em `flowbuilder.py` para:

- Alterar parâmetros de paginação
- Adicionar filtros específicos
- Modificar a fonte de dados

### Personalizando Validações

Adicione validações específicas em `DataValidationStep`:

```python
def execute(self, data: pd.DataFrame) -> StepResult:
    validation_errors = []
    
    # Suas validações personalizadas
    if 'campo_obrigatorio' not in data.columns:
        validation_errors.append("Campo obrigatório ausente")
    
    # ... resto da validação
```

## Desenvolvimento

### Executando Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Executar testes específicos
pytest tests/test_steps.py -v

# Executar com coverage
pytest tests/ --cov={project_name} --cov-report=html
```

### Estrutura dos Testes

- `test_steps.py`: Testes dos steps individuais
- `test_flowbuilder.py`: Testes do FlowBuilder
- `test_main.py`: Testes da função principal
- `conftest.py`: Fixtures compartilhadas

### Debugging

Para debugar o pipeline:

```python
from {project_name} import {project_class_name}FlowBuilder

builder = {project_class_name}FlowBuilder()

# Executar step por step
builder.set_date_reference(datetime.now())
builder.collect()

# Verificar dados coletados
print(f"Dados coletados: {{len(builder.current_data)}}")
print(builder.current_data.head())

# Continuar processamento
builder.process()

# Verificar resultados
for result in builder.get_results():
    print(f"{{result.success}}: {{result.message}}")
```

## Monitoramento

### Logs

O pipeline usa logging padrão do Python. Para configurar:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Métricas

O `FlowBuilder` coleta métricas automáticas:

- Tempo de execução de cada step
- Número de registros processados
- Erros e avisos
- Metadados de execução

## Troubleshooting

### Problemas Comuns

1. **Erro de conexão com Sankhya**
   - Verifique as credenciais no `.env`
   - Confirme a URL da API
   - Verifique conectividade de rede

2. **Erro de salvamento**
   - Verifique permissões no Azure Storage
   - Confirme configurações do banco de dados
   - Verifique se a entidade de destino está configurada

3. **Dados não coletados**
   - Verifique filtros de data
   - Confirme parâmetros de paginação
   - Verifique logs de erro

### Logs de Debug

Para logs detalhados:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Executar pipeline
result = main()
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes
5. Submeta um pull request

## Licença

Este projeto está sob a licença MIT.
'''
