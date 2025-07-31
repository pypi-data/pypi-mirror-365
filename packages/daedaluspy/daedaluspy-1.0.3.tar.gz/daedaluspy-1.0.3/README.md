# DaedalusPy

## Visão Geral
DaedalusPy é um framework para engenharia de dados, criado para acelerar a construção de bibliotecas de dados corporativas e pipelines analíticos modulares, com foco em padronização, governança, reuso e produtividade em ambientes cloud ou multi-cloud.

Pensando principalmente para utilização junto a ferramentas como azure synapse, Databricks e outros serviços de dados em nuvem, DaedalusPy permite que engenheiros de dados criem soluções robustas e escaláveis com facilidade.

Com o foco em trazer 2 grandes blocos de funcionalidades:

## Bibliotecas de Dados Corporativas

Bibliotecas de dados unificadas centralizam entidades, domínios, validações e funções reutilizáveis, promovendo o reuso e a governança de dados em toda a organização. Recomendamos que profissionais próximos ao DevOps criem e disponibilizem essas bibliotecas para os engenheiros de dados mais próximos do desenvolvimento dos pipelines, assegurando que todos sigam padrões e práticas recomendadas de forma consistente.

Embora o foco principal seja a biblioteca de dados, incentivamos que ela — assim como o datalake — seja tratada como um middleware estratégico. Dessa forma, todos os processos que dependem de dados na empresa passam a adotar uma linguagem de negócio única, independentemente de onde os dados estejam armazenados.

## Pipelines Analíticos Modulares

Pipelines analíticos modulares permitem a construção de fluxos de trabalho complexos de maneira simples, reutilizável e escalável. Com componentes desacoplados e altamente configuráveis, os engenheiros de dados podem orquestrar processos de ETL, transformação e análise de dados de forma eficiente, adaptando rapidamente as soluções às necessidades do negócio.

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
     daedaluspy create-lib <nome> [--dataname <entidade>] [--systemname <domínio>]
     ```
   - **Argumentos:**
     - `<nome>`: Nome da biblioteca (obrigatório).
     - `--dataname <entidade>`: (Opcional) Nome da entidade principal a ser criada junto com a biblioteca.
     - `--systemname <domínio>`: (Opcional) Nome do domínio/sistema principal.
   - **Exemplo:**
     ```bash
     daedaluspy create-lib corp_data --dataname ClienteEntity --systemname vendas
     ```
   - **Como funciona:** Gera uma pasta `<libname>/` com subpastas para `config/`, `data/`, `service/`, `tools/` e arquivos essenciais. Isso garante que todo projeto siga o mesmo padrão e facilite o reuso entre times.
   - **Quando usar:** Sempre que iniciar um novo domínio de dados ou projeto analítico.

2. **Geração de Entidades de Dados**
   - **O que faz:** Cria classes de entidades de negócio (ex: ClienteEntity) já com estrutura OOP, enums, validações e templates prontos para uso.
   - **Comando:**
     ```bash
     daedaluspy create-data <ClasseEntidade> --tier <raw|clear|model> --cloud <azure|aws|google> [--columns <col1:tipo,col2:tipo,...>] [--output <pasta>]
     ```
   - **Argumentos:**
     - `<ClasseEntidade>`: Nome da classe da entidade (obrigatório, ex: ClienteEntity).
     - `--tier <raw|clear|model>`: Camada da entidade (obrigatório).
     - `--cloud <azure|aws|google>`: Provedor cloud de referência (obrigatório).
     - `--columns <col1:tipo,col2:tipo,...>`: (Opcional) Lista de colunas e tipos, separadas por vírgula (ex: nome:str,idade:int).
     - `--output <pasta>`: (Opcional) Caminho de saída para o arquivo gerado.
   - **Exemplo:**
     ```bash
     daedaluspy create-data ClienteEntity --tier raw --cloud azure --columns nome:str,idade:int,email:str
     ```
   - **Como funciona:** Gera arquivos Python na estrutura correta, com métodos, validações e documentação, prontos para serem usados em pipelines e serviços.
   - **Quando usar:** Sempre que precisar modelar uma nova entidade de dados, seja para ingestão, transformação ou consumo.

3. **Geração de Serviços**
   - **O que faz:** Cria serviços de integração (ex: APIs, bancos de dados) já integrados à biblioteca, seguindo padrões de OOP e enums.
   - **Comando:**
     ```bash
     daedaluspy create-service <NomeServico> --type <api|database> [--models <Model1,Model2,...>] [--output <pasta>]
     ```
   - **Argumentos:**
     - `<NomeServico>`: Nome do serviço (obrigatório).
     - `--type <api|database>`: Tipo do serviço (obrigatório).
     - `--output <pasta>`: (Opcional) Caminho de saída para o serviço gerado.
   - **Exemplo:**
     ```bash
     daedaluspy create-service Salesforce --type api
     ```
   - **Como funciona:** Gera a estrutura de serviço, facilitando integrações externas e padronizando o acesso a dados.
   - **Quando usar:** Sempre que precisar integrar uma nova fonte ou destino de dados ao seu ecossistema.

4. **Geração de Pipelines**
   - **O que faz:** Cria a estrutura de um pipeline modular, pronto para orquestração, sem subpastas desnecessárias e com todos os arquivos essenciais (main, config, steps, etc).
   - **Comando:**
     ```bash
     daedaluspy create-pipeline <domínio> <entidade> --tier <raw|clear|model> --output <pasta> [--template_type <tipo>] [--lib_name <nome>] [--cloud_provider <cloud>] [--entity_target <entidade>] [--entity_target_class <classe>]
     ```
   - **Argumentos:**
     - `<domínio>`: Nome do domínio do pipeline (obrigatório).
     - `<entidade>`: Nome da entidade principal (obrigatório).
     - `--tier <raw|clear|model>`: Camada do pipeline (obrigatório).
     - `--output <pasta>`: Caminho de saída do pipeline (obrigatório), recomendamos em caso de azure synapse, sparkJobsFiles.
     - `--lib_name <nome>`: (Opcional) Nome da biblioteca de dados a ser referenciada, caso tenha mais de uma biblioteca na mesma pasta.
     - `--cloud_provider <cloud>`: (Opcional) Provedor cloud de referência, opções sendo: azure, aws, google.
     - `--entity_target <entidade>`: (Opcional) Entidade alvo para integração.
     - `--entity_target_class <classe>`: (Opcional) Classe da entidade alvo.
   - **Exemplo:**
     ```bash
     daedaluspy create-pipeline vendas ClienteEntity --tier clear --output ./vendas_pipeline --template_type etl --lib_name corp_data --cloud_provider azure
     ```
   - **Como funciona:** Gera uma pasta do pipeline diretamente no local especificado, pronta para receber a lógica de negócio e ser executada.
   - **Quando usar:** Sempre que precisar criar um novo fluxo de ingestão, transformação ou entrega de dados, reaproveitando entidades e serviços da biblioteca.

---

Cada comando do DaedalusPy foi desenhado para garantir padronização, acelerar o desenvolvimento e permitir que o engenheiro de dados foque no que realmente importa: a lógica de negócio e a entrega de valor. O CLI não substitui o trabalho do desenvolvedor, mas elimina o retrabalho estrutural e direciona o padrão arquitetural do projeto.

## Casos de Uso Reais

- **Criar biblioteca de dados corporativa:**
  ```bash
  daedaluspy create-lib corp_data
  ```

- **Adicionar entidade de negócio:**
  ```bash
  daedaluspy create-data ClienteEntity --tier raw --cloud azure
  ```

- **Adicionar serviço de integração:**
  ```bash
  daedaluspy create-service Salesforce --type api
  ```

- **Gerar pipeline para domínio/entidade/camada:**
  ```bash
  daedaluspy create-pipeline vendas ClienteEntity --tier clear --output .
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
  steps.py
  main.py
  README.md
  requirements.txt
```

## Fluxo de Trabalho Típico

1. **Crie a biblioteca:**  
   `daedaluspy create-lib corp_data`
2. **Adicione entidades e serviços:**  
   `daedaluspy create-data ClienteEntity --tier raw --cloud azure`  
   `daedaluspy create-service Salesforce --type api`
3. **Gere o pipeline:**  
   `daedaluspy create-pipeline vendas ClienteEntity --tier clear --output .`
4. **Implemente lógica e execute.**


## Melhores Práticas
- Use o CLI para gerar a estrutura base e arquivos padronizados.
- Implemente a lógica de negócio, transformações e integrações nos arquivos gerados.
- Siga os padrões do desenvolvimento orientado a objetos (OOP) e templates definidos pelo framework.
- Evite alterar manualmente a estrutura dos arquivos base gerados pelo CLI (exceto para lógica de negócio).
- Mantenha a biblioteca centralizada e versionada.
- Use templates para padronizar lógica e documentação.

## Público-Alvo
- Engenheiros e arquitetos de dados
- Times de analytics, BI e governança

## Licença
MIT