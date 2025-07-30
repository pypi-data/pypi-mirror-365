# DaedalusPy

## Visão Geral
DaedalusPy é um framework open-source para engenharia de dados, criado para acelerar a construção de bibliotecas de dados corporativas e pipelines analíticos modulares, com foco em padronização, governança, reuso e produtividade em ambientes multi-cloud.

## Objetivos
- Padronizar a modelagem, transformação e integração de dados em projetos analíticos.
- Centralizar entidades, domínios, validações e funções reutilizáveis.
- Facilitar a construção, orquestração e manutenção de pipelines robustos e escaláveis.
- Promover governança, versionamento e documentação centralizada.

## Macro Entregas (Explicação Detalhada)

1. **Geração de Bibliotecas de Dados**
   - **O que faz:** Cria a estrutura base de uma biblioteca de dados corporativa, centralizando entidades, configurações, serviços e ferramentas reutilizáveis.
   - **Comando:**
     ```bash
     python -m daedaluspy.cli create-lib <nome> [--dataname <entidade>] [--systemname <domínio>]
     ```
   - **Como funciona:** Gera uma pasta `<libname>/` com subpastas para `config/`, `data/`, `service/`, `tools/` e arquivos essenciais. Isso garante que todo projeto siga o mesmo padrão e facilite o reuso entre times.
   - **Quando usar:** Sempre que iniciar um novo domínio de dados ou projeto analítico.

2. **Geração de Entidades de Dados**
   - **O que faz:** Cria classes de entidades de negócio (ex: ClienteEntity) já com estrutura OOP, enums, validações e templates prontos para uso.
   - **Comando:**
     ```bash
     python -m daedaluspy.cli create-data <ClasseEntidade> --tier <raw|clear|model> --cloud <azure|aws|google> [--columns ...]
     ```
   - **Como funciona:** Gera arquivos Python na estrutura correta, com métodos, validações e documentação, prontos para serem usados em pipelines e serviços.
   - **Quando usar:** Sempre que precisar modelar uma nova entidade de dados, seja para ingestão, transformação ou consumo.

3. **Geração de Serviços**
   - **O que faz:** Cria serviços de integração (ex: APIs, bancos de dados) já integrados à biblioteca, seguindo padrões de OOP e enums.
   - **Comando:**
     ```bash
     python -m daedaluspy.cli create-service <NomeServico> --type <api|database> [--models ...]
     ```
   - **Como funciona:** Gera a estrutura de serviço, facilitando integrações externas e padronizando o acesso a dados.
   - **Quando usar:** Sempre que precisar integrar uma nova fonte ou destino de dados ao seu ecossistema.

4. **Geração de Pipelines**
   - **O que faz:** Cria a estrutura de um pipeline modular, pronto para orquestração, sem subpastas desnecessárias e com todos os arquivos essenciais (main, config, steps, etc).
   - **Comando:**
     ```bash
     python -m daedaluspy.cli create-pipeline <domínio> <entidade> --tier <raw|clear|model> --output <pasta> [--template_type ...] [--lib_name ...] [--cloud_provider ...] [--entity_target ...] [--entity_target_class ...]
     ```
   - **Como funciona:** Gera uma pasta do pipeline diretamente no local especificado, pronta para receber a lógica de negócio e ser executada.
   - **Quando usar:** Sempre que precisar criar um novo fluxo de ingestão, transformação ou entrega de dados, reaproveitando entidades e serviços da biblioteca.

---

Cada comando do DaedalusPy foi desenhado para garantir padronização, acelerar o desenvolvimento e permitir que o engenheiro de dados foque no que realmente importa: a lógica de negócio e a entrega de valor. O CLI não substitui o trabalho do desenvolvedor, mas elimina o retrabalho estrutural e direciona o padrão arquitetural do projeto.

## Casos de Uso Reais

- **Criar biblioteca de dados corporativa:**
  ```bash
  python -m daedaluspy.cli create-lib corp_data
  ```

- **Adicionar entidade de negócio:**
  ```bash
  python -m daedaluspy.cli create-data ClienteEntity --tier raw --cloud azure
  ```

- **Adicionar serviço de integração:**
  ```bash
  python -m daedaluspy.cli create-service Salesforce --type api
  ```

- **Gerar pipeline para domínio/entidade/camada:**
  ```bash
  python -m daedaluspy.cli create-pipeline vendas ClienteEntity --tier clear --output .
  ```

## Estrutura Gerada (Exemplo Real)

```
corp_data/
  config/
    __init__.py
    config.py
  data/
    raw/
      __init__.py
      ClienteEntity.py
    clear/
    model/
  service/
    salesforce/
      __init__.py
  tools/
    logger/
      __init__.py
  __init__.py
  README.md
  setup.py

vendas_ClienteEntity_clear/
  __init__.py
  base.py
  config.py
  flowbuilder.py
  main.py
  README.md
  requirements.txt
  steps.py
```

## Fluxo de Trabalho Típico

1. **Crie a biblioteca:**  
   `python -m daedaluspy.cli create-lib corp_data`
2. **Adicione entidades e serviços:**  
   `python -m daedaluspy.cli create-data ClienteEntity --tier raw --cloud azure`  
   `python -m daedaluspy.cli create-service Salesforce --type api`
3. **Gere o pipeline:**  
   `python -m daedaluspy.cli create-pipeline vendas ClienteEntity --tier clear --output .`
4. **Implemente lógica e execute.**

## Integração e Extensibilidade
- Suporte a múltiplos clouds e bancos.
- Templates customizáveis.
- Código OOP, enums e tipagem forte.
- CLI extensível para novos comandos.

## Melhores Práticas
- Use o CLI para gerar a estrutura base e arquivos padronizados.
- Implemente a lógica de negócio, transformações e integrações nos arquivos gerados.
- Siga os padrões de OOP, enums e templates definidos pelo framework.
- Evite alterar manualmente a estrutura dos arquivos base gerados pelo CLI (exceto para lógica de negócio).
- Mantenha a biblioteca centralizada e versionada.
- Use templates para padronizar lógica e documentação.

## Público-Alvo
- Engenheiros e arquitetos de dados
- Times de analytics, BI e governança
- Projetos que exigem padronização, reuso e automação

## Licença
MIT
