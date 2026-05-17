````markdown
# Arquitetura do Projeto

## Visão geral

Este projeto implementa uma pipeline batch de Engenharia de Dados para processar despesas parlamentares de deputados federais a partir da API Dados Abertos da Câmara dos Deputados.

A arquitetura foi construída com separação em camadas, seguindo uma abordagem comum em pipelines analíticas:

- **Bronze**: dados brutos;
- **Silver**: dados tratados;
- **Gold**: dados modelados para análise.

O pipeline é executado localmente com Python e orquestrado com Apache Airflow em Docker. As camadas Bronze e Silver são enviadas para o Google Cloud Storage, enquanto a camada Gold é materializada no BigQuery.

---

## Fluxo macro da arquitetura

```text
API Dados Abertos Câmara
        ↓
Extração com Python
        ↓
Bronze Local - JSON bruto
        ↓
Transformação com Pandas
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
````

---

## Componentes principais

| Componente               | Função                                     |
| ------------------------ | ------------------------------------------ |
| API Dados Abertos Câmara | Fonte de dados do projeto                  |
| Python                   | Extração, transformação, validação e carga |
| Requests                 | Consumo dos endpoints da API               |
| Pandas                   | Tratamento e padronização dos dados        |
| PyArrow                  | Escrita e leitura de arquivos Parquet      |
| Google Cloud Storage     | Data Lake em nuvem                         |
| BigQuery                 | Data Warehouse analítico                   |
| Apache Airflow           | Orquestração do pipeline                   |
| Docker                   | Ambiente isolado para execução do Airflow  |
| SQL                      | Modelagem Gold e views analíticas          |
| Git/GitHub               | Versionamento e portfólio                  |

---

## Camada Bronze

A camada Bronze armazena os dados exatamente como foram recebidos da API.

### Objetivo

Preservar o dado bruto para auditoria, rastreabilidade e possibilidade de reprocessamento.

### Características

* formato JSON;
* dados sem tratamento;
* estrutura original preservada;
* organização por entidade e data de carga;
* armazenamento local e em nuvem;
* base para geração da camada Silver.

### Estrutura local

```text
data/raw/bronze/
├── deputados/
│   └── dt_carga=YYYY-MM-DD/
│       └── deputados.json
└── despesas/
    └── ano=YYYY/
        └── mes=MM/
            └── dt_carga=YYYY-MM-DD/
                └── despesas.json
```

### Estrutura no Google Cloud Storage

```text
gs://etl-camara-deputados-luis-2026-data-lake/bronze/
```

---

## Camada Silver

A camada Silver contém os dados tratados, padronizados e deduplicados.

### Objetivo

Criar uma versão limpa e estruturada dos dados, adequada para carga em ferramentas analíticas e data warehouses.

### Características

* formato Parquet;
* colunas padronizadas em `snake_case`;
* conversão de tipos numéricos;
* conversão de datas;
* remoção de duplicidades técnicas;
* inclusão de colunas de controle;
* armazenamento local e em nuvem;
* base para carga no BigQuery.

### Estrutura local

```text
data/processed/silver/
├── deputados/
│   └── deputados.parquet
└── despesas/
    └── ano=YYYY/
        └── mes=MM/
            └── despesas.parquet
```

### Estrutura no Google Cloud Storage

```text
gs://etl-camara-deputados-luis-2026-data-lake/silver/
```

---

## Camada Gold

A camada Gold é criada no BigQuery e contém dados prontos para análise.

### Objetivo

Disponibilizar tabelas modeladas e views analíticas para consultas, exploração dos dados e construção de dashboards.

### Tabelas Gold

```text
dim_deputado
dim_partido
dim_fornecedor
dim_tipo_despesa
fato_despesas
```

### Views analíticas

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

## Modelo dimensional

O modelo analítico segue uma estrutura simples com tabela fato e dimensões.

```text
dim_deputado
dim_partido
dim_fornecedor
dim_tipo_despesa
        ↓
fato_despesas
```

### Tabela fato

A tabela `fato_despesas` concentra os eventos financeiros de despesas parlamentares.

Ela contém informações como:

* deputado;
* ano e mês;
* tipo de despesa;
* documento fiscal;
* fornecedor;
* valores financeiros;
* lote;
* parcela;
* data do documento;
* data de carga.

### Dimensões

As dimensões fornecem contexto para análise por:

* deputado;
* partido;
* unidade federativa;
* fornecedor;
* tipo de despesa.

---

## Orquestração

A orquestração é feita com Apache Airflow em ambiente Docker.

### DAG principal

```text
camara_deputados_etl_dag
```

### Fluxo da DAG

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

Cada task executa uma etapa do pipeline utilizando os scripts Python do projeto.

### Responsabilidade das tasks

| Task                           | Responsabilidade                        |
| ------------------------------ | --------------------------------------- |
| `extract`                      | Extrair deputados e despesas da API     |
| `transform`                    | Gerar arquivos tratados em Parquet      |
| `quality_checks`               | Validar integridade da camada Silver    |
| `upload_gcs_and_load_bigquery` | Enviar dados ao GCS e carregar BigQuery |
| `run_gold_sql`                 | Criar tabelas Gold e views analíticas   |

---

## Integração com Google Cloud

### Google Cloud Storage

O GCS funciona como Data Lake em nuvem do projeto.

O bucket utilizado armazena:

```text
bronze/
silver/
gold/
```

A camada `gold/` foi reservada para expansões futuras, enquanto a camada Gold atual é materializada diretamente no BigQuery.

### BigQuery

O BigQuery funciona como Data Warehouse analítico.

O dataset principal é:

```text
camara_analytics
```

Ele armazena:

* tabelas staging carregadas a partir da camada Silver;
* tabelas dimensionais;
* tabela fato;
* views analíticas para consumo.

---

## Configuração do bucket

O bucket foi criado com configuração enxuta para reduzir risco de custo.

| Configuração                | Valor         |
| --------------------------- | ------------- |
| Região                      | `us-central1` |
| Tipo de localidade          | Regional      |
| Classe de armazenamento     | `STANDARD`    |
| Versionamento               | Desativado    |
| Soft delete                 | Desativado    |
| Uniform bucket-level access | Ativado       |

---

## Segurança

O projeto aplica boas práticas básicas de segurança para ambiente de desenvolvimento e portfólio.

### Práticas adotadas

* arquivo `.env` não versionado;
* pasta `credentials/` não versionada;
* uso de Service Account para autenticação GCP;
* credencial local fora do repositório;
* bucket com acesso uniforme;
* ausência de arquivos sensíveis no GitHub;
* variáveis de ambiente centralizadas;
* separação entre configuração local e código-fonte.

---

## Quality Checks

Antes da carga para GCS e BigQuery, a camada Silver passa por validações locais.

### Validações aplicadas

* existência dos arquivos Parquet;
* verificação de tabelas não vazias;
* validação de colunas obrigatórias;
* validação de campos críticos não nulos;
* coerência de ano e mês;
* validação de valores monetários numéricos;
* verificação de duplicidades técnicas.

Valores negativos em despesas são mantidos como `warning`, pois podem representar estornos, ajustes ou devoluções.

---

## Decisões arquiteturais

### Uso de Airflow local

Foi escolhido Airflow local com Docker para evitar custos de serviços gerenciados, como Cloud Composer, mantendo a prática de orquestração profissional.

### Uso de Parquet

O formato Parquet foi escolhido para a camada Silver por ser colunar, eficiente e adequado para pipelines analíticas.

### Uso de GCS

O Cloud Storage foi utilizado como Data Lake em nuvem para armazenar as camadas Bronze e Silver.

### Uso de BigQuery

O BigQuery foi utilizado como Data Warehouse para modelagem Gold e consumo analítico.

### Uso de Docker

O Docker foi utilizado para isolar o ambiente do Airflow e evitar instalação direta de suas dependências no ambiente virtual principal do projeto.

---

## Considerações de custo

O projeto evita recursos com custo persistente elevado.

### Recursos evitados no MVP

* Cloud Composer;
* máquinas virtuais;
* Dataflow;
* Cloud SQL;
* serviços gerenciados sempre ativos.

### Recursos utilizados

* Google Cloud Storage;
* BigQuery;
* Service Account;
* Airflow local com Docker.

Essa abordagem mantém a arquitetura próxima de um cenário profissional, mas com baixo custo operacional.

---

## Evidências visuais

As evidências visuais do projeto estão armazenadas em:

```text
docs/images/

---

## Status da arquitetura

| Componente               | Status       |
| ------------------------ | ------------ |
| Extração da API          | Implementado |
| Bronze local             | Implementado |
| Silver local             | Implementado |
| Quality checks           | Implementado |
| Upload para GCS          | Implementado |
| Carga no BigQuery        | Implementado |
| Camada Gold              | Implementado |
| Views analíticas         | Implementado |
| Orquestração com Airflow | Implementado |
| Dashboard                | Pendente     |

```
```
