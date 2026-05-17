````markdown
# ETL Despesas Parlamentares no GCP

Pipeline de Engenharia de Dados para extração, tratamento, validação, armazenamento e análise de despesas parlamentares de deputados federais, utilizando dados públicos da Câmara dos Deputados.

O projeto implementa uma arquitetura batch ponta a ponta com Python, Apache Airflow, Docker, Google Cloud Storage, BigQuery e SQL analítico, seguindo uma organização em camadas Bronze, Silver e Gold.

---

## Sumário

- [Objetivo](#objetivo)
- [Fonte de dados](#fonte-de-dados)
- [Arquitetura](#arquitetura)
- [Stack utilizada](#stack-utilizada)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Camadas de dados](#camadas-de-dados)
- [Modelo analítico](#modelo-analítico)
- [Orquestração com Airflow](#orquestração-com-airflow)
- [Execução local](#execução-local)
- [Execução com Docker e Airflow](#execução-com-docker-e-airflow)
- [Tabelas e views no BigQuery](#tabelas-e-views-no-bigquery)
- [Resultados validados](#resultados-validados)
- [Segurança e boas práticas](#segurança-e-boas-práticas)
- [Próximas melhorias](#próximas-melhorias)
- [Autor](#autor)

---

## Objetivo

Construir uma pipeline de dados completa para processar despesas parlamentares de deputados federais, desde a extração dos dados na API pública até a disponibilização de tabelas e views analíticas no BigQuery.

A pipeline contempla:

- extração de dados via API REST;
- armazenamento dos dados brutos em camada Bronze;
- tratamento e padronização dos dados em camada Silver;
- validações de qualidade de dados;
- upload das camadas Bronze e Silver para o Google Cloud Storage;
- carga dos arquivos Parquet no BigQuery;
- criação de tabelas dimensionais e tabela fato na camada Gold;
- criação de views analíticas para dashboard;
- orquestração com Apache Airflow em ambiente Docker;
- documentação técnica para portfólio de Engenharia de Dados.

---

## Fonte de dados

A fonte utilizada é a API Dados Abertos da Câmara dos Deputados.

Endpoints principais utilizados:

```text
/deputados
/deputados/{id}/despesas
````

O escopo inicial do MVP considera um recorte parametrizável por ano, mês e quantidade de deputados processados.

Exemplo do recorte utilizado na validação:

```text
Ano: 2026
Mês: 03
Limite inicial: 5 deputados
```

---

## Arquitetura

```text
API Dados Abertos Câmara
        ↓
Extract - Python Requests
        ↓
Bronze Local - JSON bruto
        ↓
Transform - Pandas + PyArrow
        ↓
Silver Local - Parquet tratado
        ↓
Quality Checks
        ↓
Google Cloud Storage
        ↓
BigQuery - Staging
        ↓
BigQuery - Gold
        ↓
Views Analíticas
        ↓
Dashboard / Análise
```

A pipeline foi desenhada com separação clara entre ingestão, transformação, validação, armazenamento cloud, carga analítica e camada de consumo.

---

## Stack utilizada

| Camada              | Tecnologias                     |
| ------------------- | ------------------------------- |
| Linguagem           | Python 3.12                     |
| Extração            | requests                        |
| Transformação       | pandas, numpy, pyarrow          |
| Qualidade de dados  | pandas, validações customizadas |
| Armazenamento local | JSON e Parquet                  |
| Data Lake cloud     | Google Cloud Storage            |
| Data Warehouse      | BigQuery                        |
| Orquestração        | Apache Airflow                  |
| Containerização     | Docker e Docker Compose         |
| Configuração        | python-dotenv                   |
| SQL analítico       | BigQuery Standard SQL           |
| Versionamento       | Git e GitHub                    |
| Ambiente            | WSL Ubuntu                      |

---

## Estrutura do projeto

```text
etl-despesas-parlamentares-gcp/
├── dags/
│   └── camara_deputados_etl_dag.py
├── data/
│   ├── raw/
│   │   └── bronze/
│   ├── processed/
│   │   └── silver/
│   └── output/
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── execution_guide.md
│   └── images/
├── sql/
│   ├── create_tables.sql
│   ├── create_views.sql
│   └── analytical_queries.sql
├── src/
│   ├── extract/
│   │   ├── api_client.py
│   │   ├── extract_deputados.py
│   │   └── extract_despesas.py
│   ├── transform/
│   │   ├── transform_deputados.py
│   │   └── transform_despesas.py
│   ├── quality/
│   │   └── checks.py
│   ├── load/
│   │   ├── upload_gcs.py
│   │   ├── load_bigquery.py
│   │   └── run_bigquery_sql.py
│   └── utils/
│       ├── config.py
│       ├── logger.py
│       └── paths.py
├── tests/
├── Dockerfile.airflow
├── docker-compose.yaml
├── requirements.txt
├── requirements-airflow.txt
├── .env.example
└── README.md
```

---

## Camadas de dados

### Bronze

A camada Bronze armazena os dados brutos retornados pela API, preservando a estrutura original dos registros.

Formato:

```text
JSON
```

Exemplos locais:

```text
data/raw/bronze/deputados/dt_carga=YYYY-MM-DD/deputados.json
data/raw/bronze/despesas/ano=2026/mes=03/dt_carga=YYYY-MM-DD/despesas.json
```

Exemplo no GCS:

```text
gs://etl-camara-deputados-luis-2026-data-lake/bronze/
```

Características:

* dados sem transformação;
* estrutura original da API;
* uso para auditoria e reprocessamento;
* organização por entidade, ano, mês e data de carga.

---

### Silver

A camada Silver armazena os dados tratados e padronizados.

Formato:

```text
Parquet
```

Exemplos locais:

```text
data/processed/silver/deputados/deputados.parquet
data/processed/silver/despesas/ano=2026/mes=03/despesas.parquet
```

Exemplo no GCS:

```text
gs://etl-camara-deputados-luis-2026-data-lake/silver/
```

Transformações aplicadas:

* padronização de nomes de colunas em `snake_case`;
* conversão de tipos numéricos;
* conversão de datas;
* inclusão de colunas de controle;
* deduplicação técnica;
* organização em formato colunar Parquet.

---

### Gold

A camada Gold é criada no BigQuery e contém tabelas modeladas para análise.

Tabelas criadas:

```text
dim_deputado
dim_partido
dim_fornecedor
dim_tipo_despesa
fato_despesas
```

Views analíticas criadas:

```text
vw_kpis_gerais
vw_ranking_deputados
vw_ranking_partidos
vw_ranking_ufs
vw_ranking_fornecedores
vw_ranking_tipos_despesa
vw_evolucao_mensal
```

---

## Modelo analítico

O modelo analítico segue uma abordagem dimensional simples, com tabela fato e dimensões de apoio.

```text
dim_deputado
dim_partido
dim_fornecedor
dim_tipo_despesa
        ↓
fato_despesas
```

### Tabela fato

A tabela `fato_despesas` concentra os eventos de despesas parlamentares, contendo:

* deputado;
* ano e mês;
* tipo de despesa;
* documento fiscal;
* fornecedor;
* valores financeiros;
* lote;
* parcela;
* data de carga.

### Dimensões

As dimensões permitem análises por:

* deputado;
* partido;
* unidade federativa;
* fornecedor;
* tipo de despesa.

---

## Orquestração com Airflow

A orquestração é feita com Apache Airflow executando localmente via Docker Compose.

DAG principal:

```text
camara_deputados_etl_dag
```

Fluxo da DAG:

```text
extract
↓
transform
↓
quality_checks
↓
upload_gcs_and_load_bigquery
↓
run_gold_sql
```

Cada task executa uma parte do pipeline por meio de comandos Python, reaproveitando os módulos do projeto.

---

## Execução local

### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

### 2. Ativar ambiente virtual

```bash
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` com base no `.env.example`.

Exemplo:

```env
GCP_PROJECT_ID=seu-projeto-gcp
GCP_BUCKET_NAME=seu-bucket-gcs
BIGQUERY_DATASET=camara_analytics
GOOGLE_APPLICATION_CREDENTIALS=credentials/sua-service-account.json
API_BASE_URL=https://dadosabertos.camara.leg.br/api/v2
DEFAULT_YEAR=2026
DEFAULT_MONTH=3
```

### 5. Executar pipeline completa

```bash
python -m src.run_pipeline --ano 2026 --mes 3 --limite-deputados 5
```

### 6. Executar sem nova extração

```bash
python -m src.run_pipeline --ano 2026 --mes 3 --skip-extract
```

---

## Execução por etapas

### Extração

```bash
python -m src.extract.extract_deputados
```

```bash
python -m src.extract.extract_despesas --ano 2026 --mes 3 --limite-deputados 5
```

### Transformação

```bash
python -m src.transform.transform_deputados
```

```bash
python -m src.transform.transform_despesas --ano 2026 --mes 3
```

### Quality checks

```bash
python -m src.quality.checks --ano 2026 --mes 3
```

### Upload para GCS

```bash
python -m src.load.upload_gcs --layer all
```

### Carga no BigQuery

```bash
python -m src.load.load_bigquery --table all --ano 2026 --mes 3
```

### Criação da camada Gold

```bash
python -m src.load.run_bigquery_sql --target all
```

---

## Execução com Docker e Airflow

### 1. Subir os containers

```bash
docker compose --env-file .env.airflow up -d
```

### 2. Acessar Airflow

```text
http://localhost:8080
```

Credenciais locais:

```text
Usuário: admin
Senha: admin
```

### 3. Executar DAG

Na interface do Airflow, localizar e executar:

```text
camara_deputados_etl_dag
```

### 4. Parar containers

```bash
docker compose --env-file .env.airflow down
```

---

## Tabelas e views no BigQuery

Dataset:

```text
camara_analytics
```

Tabelas base carregadas a partir da camada Silver:

```text
deputados
despesas
```

Tabelas Gold:

```text
dim_deputado
dim_partido
dim_fornecedor
dim_tipo_despesa
fato_despesas
```

Views analíticas:

```text
vw_kpis_gerais
vw_ranking_deputados
vw_ranking_partidos
vw_ranking_ufs
vw_ranking_fornecedores
vw_ranking_tipos_despesa
vw_evolucao_mensal
```

Exemplo de consulta:

```sql
SELECT *
FROM `etl-camara-deputados-luis-2026.camara_analytics.vw_kpis_gerais`;
```

---

## Quality checks

As validações locais verificam:

* existência dos arquivos Parquet;
* tabelas não vazias;
* colunas obrigatórias;
* nulos em campos críticos;
* coerência de ano e mês;
* valores monetários numéricos;
* duplicidades técnicas.

Valores negativos em despesas são tratados como `warning`, pois podem representar estornos, ajustes ou devoluções.

---

## Resultados validados

No recorte inicial processado:

```text
Ano: 2026
Mês: 03
Deputados processados na extração de despesas: 5
```

Indicadores validados:

| Métrica                           |         Valor |
| --------------------------------- | ------------: |
| Deputados carregados              |           513 |
| Despesas tratadas                 |           146 |
| Deputados com despesas no recorte |             5 |
| Fornecedores únicos               |            84 |
| Tipos de despesa                  |            11 |
| Total valor documento             | R$ 251.384,89 |
| Total valor líquido               | R$ 251.253,99 |
| Total valor glosa                 |     R$ 130,90 |
| Média valor líquido               |   R$ 1.720,92 |

---

## Segurança e boas práticas

Boas práticas aplicadas no projeto:

* `.env` não versionado;
* credenciais GCP fora do Git;
* uso de Service Account;
* bucket GCS com acesso uniforme;
* versionamento do bucket desativado;
* soft delete desativado;
* Airflow executado localmente via Docker;
* ausência de Cloud Composer no MVP para evitar custos desnecessários;
* separação clara entre Bronze, Silver e Gold;
* logs estruturados;
* retries em chamadas à API;
* execução parametrizável por ano, mês e limite de deputados.

---

## Comandos úteis

### Ver containers ativos

```bash
docker ps
```

### Ver logs do Airflow Scheduler

```bash
docker compose --env-file .env.airflow logs -f airflow-scheduler
```

### Listar arquivos no GCS

```bash
gcloud storage ls --recursive gs://etl-camara-deputados-luis-2026-data-lake
```

### Listar tabelas do BigQuery

```bash
bq ls etl-camara-deputados-luis-2026:camara_analytics
```

### Consultar KPIs no BigQuery

```bash
bq query --use_legacy_sql=false \
'SELECT * FROM `etl-camara-deputados-luis-2026.camara_analytics.vw_kpis_gerais`'
```

---

## Status do projeto

| Fase                     | Status       |
| ------------------------ | ------------ |
| Extração via API         | Concluída    |
| Camada Bronze local      | Concluída    |
| Camada Silver local      | Concluída    |
| Quality checks           | Concluída    |
| Upload para GCS          | Concluída    |
| Carga no BigQuery        | Concluída    |
| Camada Gold BigQuery     | Concluída    |
| Views analíticas         | Concluída    |
| Orquestração com Airflow | Concluída    |
| Dashboard                | Pendente     |
| Documentação final       | Em andamento |

---

## Próximas melhorias

* Expandir o processamento para todos os deputados.
* Processar múltiplos meses e anos.
* Criar dashboard no Looker Studio.
* Criar dashboard no Power BI.
* Adicionar testes automatizados com pytest.
* Adicionar alertas de falha no Airflow.
* Melhorar particionamento e clusterização das tabelas no BigQuery.
* Implementar CI/CD com GitHub Actions.
* Criar documentação visual da arquitetura.
* Avaliar execução em ambiente cloud gerenciado em etapa futura.

---

## Autor

Desenvolvido por Luis Almeida.

GitHub: [Almeida1BR](https://github.com/Almeida1BR)

```
```
````markdown
# ETL Despesas Parlamentares no GCP

Pipeline de Engenharia de Dados para extração, tratamento, validação, armazenamento e análise de despesas parlamentares de deputados federais, utilizando dados públicos da Câmara dos Deputados.

O projeto implementa uma arquitetura batch ponta a ponta com Python, Apache Airflow, Docker, Google Cloud Storage, BigQuery e SQL analítico, seguindo uma organização em camadas Bronze, Silver e Gold.

---

## Sumário

- [Objetivo](#objetivo)
- [Fonte de dados](#fonte-de-dados)
- [Arquitetura](#arquitetura)
- [Stack utilizada](#stack-utilizada)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Camadas de dados](#camadas-de-dados)
- [Modelo analítico](#modelo-analítico)
- [Orquestração com Airflow](#orquestração-com-airflow)
- [Execução local](#execução-local)
- [Execução com Docker e Airflow](#execução-com-docker-e-airflow)
- [Tabelas e views no BigQuery](#tabelas-e-views-no-bigquery)
- [Resultados validados](#resultados-validados)
- [Segurança e boas práticas](#segurança-e-boas-práticas)
- [Próximas melhorias](#próximas-melhorias)
- [Autor](#autor)

---

## Objetivo

Construir uma pipeline de dados completa para processar despesas parlamentares de deputados federais, desde a extração dos dados na API pública até a disponibilização de tabelas e views analíticas no BigQuery.

A pipeline contempla:

- extração de dados via API REST;
- armazenamento dos dados brutos em camada Bronze;
- tratamento e padronização dos dados em camada Silver;
- validações de qualidade de dados;
- upload das camadas Bronze e Silver para o Google Cloud Storage;
- carga dos arquivos Parquet no BigQuery;
- criação de tabelas dimensionais e tabela fato na camada Gold;
- criação de views analíticas para dashboard;
- orquestração com Apache Airflow em ambiente Docker;
- documentação técnica para portfólio de Engenharia de Dados.

---

## Fonte de dados

A fonte utilizada é a API Dados Abertos da Câmara dos Deputados.

Endpoints principais utilizados:

```text
/deputados
/deputados/{id}/despesas
````

O escopo inicial do MVP considera um recorte parametrizável por ano, mês e quantidade de deputados processados.

Exemplo do recorte utilizado na validação:

```text
Ano: 2026
Mês: 03
Limite inicial: 5 deputados
```

---

## Arquitetura

```text
API Dados Abertos Câmara
        ↓
Extract - Python Requests
        ↓
Bronze Local - JSON bruto
        ↓
Transform - Pandas + PyArrow
        ↓
Silver Local - Parquet tratado
        ↓
Quality Checks
        ↓
Google Cloud Storage
        ↓
BigQuery - Staging
        ↓
BigQuery - Gold
        ↓
Views Analíticas
        ↓
Dashboard / Análise
```

A pipeline foi desenhada com separação clara entre ingestão, transformação, validação, armazenamento cloud, carga analítica e camada de consumo.

---

## Stack utilizada

| Camada              | Tecnologias                     |
| ------------------- | ------------------------------- |
| Linguagem           | Python 3.12                     |
| Extração            | requests                        |
| Transformação       | pandas, numpy, pyarrow          |
| Qualidade de dados  | pandas, validações customizadas |
| Armazenamento local | JSON e Parquet                  |
| Data Lake cloud     | Google Cloud Storage            |
| Data Warehouse      | BigQuery                        |
| Orquestração        | Apache Airflow                  |
| Containerização     | Docker e Docker Compose         |
| Configuração        | python-dotenv                   |
| SQL analítico       | BigQuery Standard SQL           |
| Versionamento       | Git e GitHub                    |
| Ambiente            | WSL Ubuntu                      |

---

## Estrutura do projeto

```text
etl-despesas-parlamentares-gcp/
├── dags/
│   └── camara_deputados_etl_dag.py
├── data/
│   ├── raw/
│   │   └── bronze/
│   ├── processed/
│   │   └── silver/
│   └── output/
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── execution_guide.md
│   └── images/
├── sql/
│   ├── create_tables.sql
│   ├── create_views.sql
│   └── analytical_queries.sql
├── src/
│   ├── extract/
│   │   ├── api_client.py
│   │   ├── extract_deputados.py
│   │   └── extract_despesas.py
│   ├── transform/
│   │   ├── transform_deputados.py
│   │   └── transform_despesas.py
│   ├── quality/
│   │   └── checks.py
│   ├── load/
│   │   ├── upload_gcs.py
│   │   ├── load_bigquery.py
│   │   └── run_bigquery_sql.py
│   └── utils/
│       ├── config.py
│       ├── logger.py
│       └── paths.py
├── tests/
├── Dockerfile.airflow
├── docker-compose.yaml
├── requirements.txt
├── requirements-airflow.txt
├── .env.example
└── README.md
```

---

## Camadas de dados

### Bronze

A camada Bronze armazena os dados brutos retornados pela API, preservando a estrutura original dos registros.

Formato:

```text
JSON
```

Exemplos locais:

```text
data/raw/bronze/deputados/dt_carga=YYYY-MM-DD/deputados.json
data/raw/bronze/despesas/ano=2026/mes=03/dt_carga=YYYY-MM-DD/despesas.json
```

Exemplo no GCS:

```text
gs://etl-camara-deputados-luis-2026-data-lake/bronze/
```

Características:

* dados sem transformação;
* estrutura original da API;
* uso para auditoria e reprocessamento;
* organização por entidade, ano, mês e data de carga.

---

### Silver

A camada Silver armazena os dados tratados e padronizados.

Formato:

```text
Parquet
```

Exemplos locais:

```text
data/processed/silver/deputados/deputados.parquet
data/processed/silver/despesas/ano=2026/mes=03/despesas.parquet
```

Exemplo no GCS:

```text
gs://etl-camara-deputados-luis-2026-data-lake/silver/
```

Transformações aplicadas:

* padronização de nomes de colunas em `snake_case`;
* conversão de tipos numéricos;
* conversão de datas;
* inclusão de colunas de controle;
* deduplicação técnica;
* organização em formato colunar Parquet.

---

### Gold

A camada Gold é criada no BigQuery e contém tabelas modeladas para análise.

Tabelas criadas:

```text
dim_deputado
dim_partido
dim_fornecedor
dim_tipo_despesa
fato_despesas
```

Views analíticas criadas:

```text
vw_kpis_gerais
vw_ranking_deputados
vw_ranking_partidos
vw_ranking_ufs
vw_ranking_fornecedores
vw_ranking_tipos_despesa
vw_evolucao_mensal
```

---

## Modelo analítico

O modelo analítico segue uma abordagem dimensional simples, com tabela fato e dimensões de apoio.

```text
dim_deputado
dim_partido
dim_fornecedor
dim_tipo_despesa
        ↓
fato_despesas
```

### Tabela fato

A tabela `fato_despesas` concentra os eventos de despesas parlamentares, contendo:

* deputado;
* ano e mês;
* tipo de despesa;
* documento fiscal;
* fornecedor;
* valores financeiros;
* lote;
* parcela;
* data de carga.

### Dimensões

As dimensões permitem análises por:

* deputado;
* partido;
* unidade federativa;
* fornecedor;
* tipo de despesa.

---

## Orquestração com Airflow

A orquestração é feita com Apache Airflow executando localmente via Docker Compose.

DAG principal:

```text
camara_deputados_etl_dag
```

Fluxo da DAG:

```text
extract
↓
transform
↓
quality_checks
↓
upload_gcs_and_load_bigquery
↓
run_gold_sql
```

Cada task executa uma parte do pipeline por meio de comandos Python, reaproveitando os módulos do projeto.

---

## Execução local

### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

### 2. Ativar ambiente virtual

```bash
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` com base no `.env.example`.

Exemplo:

```env
GCP_PROJECT_ID=seu-projeto-gcp
GCP_BUCKET_NAME=seu-bucket-gcs
BIGQUERY_DATASET=camara_analytics
GOOGLE_APPLICATION_CREDENTIALS=credentials/sua-service-account.json
API_BASE_URL=https://dadosabertos.camara.leg.br/api/v2
DEFAULT_YEAR=2026
DEFAULT_MONTH=3
```

### 5. Executar pipeline completa

```bash
python -m src.run_pipeline --ano 2026 --mes 3 --limite-deputados 5
```

### 6. Executar sem nova extração

```bash
python -m src.run_pipeline --ano 2026 --mes 3 --skip-extract
```

---

## Execução por etapas

### Extração

```bash
python -m src.extract.extract_deputados
```

```bash
python -m src.extract.extract_despesas --ano 2026 --mes 3 --limite-deputados 5
```

### Transformação

```bash
python -m src.transform.transform_deputados
```

```bash
python -m src.transform.transform_despesas --ano 2026 --mes 3
```

### Quality checks

```bash
python -m src.quality.checks --ano 2026 --mes 3
```

### Upload para GCS

```bash
python -m src.load.upload_gcs --layer all
```

### Carga no BigQuery

```bash
python -m src.load.load_bigquery --table all --ano 2026 --mes 3
```

### Criação da camada Gold

```bash
python -m src.load.run_bigquery_sql --target all
```

---

## Execução com Docker e Airflow

### 1. Subir os containers

```bash
docker compose --env-file .env.airflow up -d
```

### 2. Acessar Airflow

```text
http://localhost:8080
```

Credenciais locais:

```text
Usuário: admin
Senha: admin
```

### 3. Executar DAG

Na interface do Airflow, localizar e executar:

```text
camara_deputados_etl_dag
```

### 4. Parar containers

```bash
docker compose --env-file .env.airflow down
```

---

## Tabelas e views no BigQuery

Dataset:

```text
camara_analytics
```

Tabelas base carregadas a partir da camada Silver:

```text
deputados
despesas
```

Tabelas Gold:

```text
dim_deputado
dim_partido
dim_fornecedor
dim_tipo_despesa
fato_despesas
```

Views analíticas:

```text
vw_kpis_gerais
vw_ranking_deputados
vw_ranking_partidos
vw_ranking_ufs
vw_ranking_fornecedores
vw_ranking_tipos_despesa
vw_evolucao_mensal
```

Exemplo de consulta:

```sql
SELECT *
FROM `etl-camara-deputados-luis-2026.camara_analytics.vw_kpis_gerais`;
```

---

## Quality checks

As validações locais verificam:

* existência dos arquivos Parquet;
* tabelas não vazias;
* colunas obrigatórias;
* nulos em campos críticos;
* coerência de ano e mês;
* valores monetários numéricos;
* duplicidades técnicas.

Valores negativos em despesas são tratados como `warning`, pois podem representar estornos, ajustes ou devoluções.

---

## Resultados validados

No recorte inicial processado:

```text
Ano: 2026
Mês: 03
Deputados processados na extração de despesas: 5
```

Indicadores validados:

| Métrica                           |         Valor |
| --------------------------------- | ------------: |
| Deputados carregados              |           513 |
| Despesas tratadas                 |           146 |
| Deputados com despesas no recorte |             5 |
| Fornecedores únicos               |            84 |
| Tipos de despesa                  |            11 |
| Total valor documento             | R$ 251.384,89 |
| Total valor líquido               | R$ 251.253,99 |
| Total valor glosa                 |     R$ 130,90 |
| Média valor líquido               |   R$ 1.720,92 |

---

## Segurança e boas práticas

Boas práticas aplicadas no projeto:

* `.env` não versionado;
* credenciais GCP fora do Git;
* uso de Service Account;
* bucket GCS com acesso uniforme;
* versionamento do bucket desativado;
* soft delete desativado;
* Airflow executado localmente via Docker;
* ausência de Cloud Composer no MVP para evitar custos desnecessários;
* separação clara entre Bronze, Silver e Gold;
* logs estruturados;
* retries em chamadas à API;
* execução parametrizável por ano, mês e limite de deputados.

---

## Comandos úteis

### Ver containers ativos

```bash
docker ps
```

### Ver logs do Airflow Scheduler

```bash
docker compose --env-file .env.airflow logs -f airflow-scheduler
```

### Listar arquivos no GCS

```bash
gcloud storage ls --recursive gs://etl-camara-deputados-luis-2026-data-lake
```

### Listar tabelas do BigQuery

```bash
bq ls etl-camara-deputados-luis-2026:camara_analytics
```

### Consultar KPIs no BigQuery

```bash
bq query --use_legacy_sql=false \
'SELECT * FROM `etl-camara-deputados-luis-2026.camara_analytics.vw_kpis_gerais`'
```

---

## Status do projeto

| Fase                     | Status       |
| ------------------------ | ------------ |
| Extração via API         | Concluída    |
| Camada Bronze local      | Concluída    |
| Camada Silver local      | Concluída    |
| Quality checks           | Concluída    |
| Upload para GCS          | Concluída    |
| Carga no BigQuery        | Concluída    |
| Camada Gold BigQuery     | Concluída    |
| Views analíticas         | Concluída    |
| Orquestração com Airflow | Concluída    |
| Dashboard                | Pendente     |
| Documentação final       | Em andamento |

---

## Próximas melhorias

* Expandir o processamento para todos os deputados.
* Processar múltiplos meses e anos.
* Criar dashboard no Looker Studio.
* Criar dashboard no Power BI.
* Adicionar testes automatizados com pytest.
* Adicionar alertas de falha no Airflow.
* Melhorar particionamento e clusterização das tabelas no BigQuery.
* Implementar CI/CD com GitHub Actions.
* Criar documentação visual da arquitetura.
* Avaliar execução em ambiente cloud gerenciado em etapa futura.

---

## Autor

Desenvolvido por Luis Almeida.

GitHub: [Almeida1BR](https://github.com/Almeida1BR)

```
```
