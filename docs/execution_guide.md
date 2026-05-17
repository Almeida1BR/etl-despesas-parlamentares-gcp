````markdown
# Guia de Execução

Este guia descreve como configurar e executar o projeto localmente, em cloud e via Apache Airflow.

---

## Pré-requisitos

Para executar este projeto, é necessário ter os seguintes componentes instalados e configurados:

- WSL Ubuntu;
- Python 3.12;
- Git;
- Docker Desktop com integração WSL;
- Google Cloud CLI;
- projeto GCP com billing habilitado;
- bucket no Google Cloud Storage;
- dataset no BigQuery;
- Service Account com permissões adequadas.

---

## Configuração inicial do ambiente

### 1. Clonar o repositório

```bash
git clone https://github.com/Almeida1BR/etl-despesas-parlamentares-gcp.git
cd etl-despesas-parlamentares-gcp
````

---

### 2. Criar ambiente virtual

```bash
python -m venv .venv
```

---

### 3. Ativar ambiente virtual

```bash
source .venv/bin/activate
```

---

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Configuração de variáveis de ambiente

O projeto utiliza um arquivo `.env` local para armazenar configurações sensíveis e variáveis de execução.

Crie o arquivo `.env` com base no `.env.example`.

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

O arquivo `.env` **não deve ser versionado**.

---

## Configuração das credenciais GCP

Crie uma pasta local para armazenar a chave da Service Account:

```bash
mkdir -p credentials
```

Coloque a chave JSON dentro da pasta:

```text
credentials/sua-service-account.json
```

A pasta `credentials/` **não deve ser versionada**.

---

## Permissões esperadas da Service Account

A Service Account utilizada pela pipeline precisa ter permissões para interagir com Cloud Storage e BigQuery.

Papéis utilizados no projeto:

| Papel                  | Uso                                          |
| ---------------------- | -------------------------------------------- |
| `Storage Object Admin` | Enviar e ler arquivos no bucket GCS          |
| `BigQuery Data Editor` | Criar e substituir tabelas no dataset        |
| `BigQuery Job User`    | Executar jobs de carga e queries no BigQuery |

---

## Execução local completa

Para executar a pipeline completa localmente:

```bash
python -m src.run_pipeline --ano 2026 --mes 3 --limite-deputados 5
```

Esse comando executa as seguintes etapas:

```text
extract
transform
quality checks
upload GCS
load BigQuery
run Gold SQL
```

---

## Execução sem nova extração

Caso os dados Bronze já existam localmente, é possível executar a pipeline sem consultar novamente a API:

```bash
python -m src.run_pipeline --ano 2026 --mes 3 --skip-extract
```

Esse modo executa:

```text
transform
quality checks
upload GCS
load BigQuery
run Gold SQL
```

---

## Execução por etapa

Também é possível executar cada etapa da pipeline separadamente.

---

### Extração de deputados

```bash
python -m src.extract.extract_deputados
```

Essa etapa consulta o endpoint `/deputados` da API da Câmara e salva o JSON bruto na camada Bronze.

---

### Extração de despesas

```bash
python -m src.extract.extract_despesas --ano 2026 --mes 3 --limite-deputados 5
```

Essa etapa consulta o endpoint `/deputados/{id}/despesas` para os deputados selecionados.

Parâmetros:

| Parâmetro            | Descrição                                  |
| -------------------- | ------------------------------------------ |
| `--ano`              | Ano de referência das despesas             |
| `--mes`              | Mês de referência das despesas             |
| `--limite-deputados` | Quantidade máxima de deputados a processar |

Para processar todos os deputados:

```bash
python -m src.extract.extract_despesas --ano 2026 --mes 3 --limite-deputados 0
```

---

### Transformação de deputados

```bash
python -m src.transform.transform_deputados
```

Essa etapa lê o JSON bruto de deputados da camada Bronze e gera o arquivo Parquet tratado na camada Silver.

---

### Transformação de despesas

```bash
python -m src.transform.transform_despesas --ano 2026 --mes 3
```

Essa etapa lê o JSON bruto de despesas da camada Bronze e gera o arquivo Parquet tratado na camada Silver.

---

### Quality checks

```bash
python -m src.quality.checks --ano 2026 --mes 3
```

Essa etapa valida os arquivos Parquet da camada Silver antes da carga para cloud.

Validações realizadas:

* existência dos arquivos;
* tabelas não vazias;
* colunas obrigatórias;
* nulos em campos críticos;
* coerência de ano e mês;
* valores monetários numéricos;
* duplicidades técnicas.

---

### Upload para Google Cloud Storage

```bash
python -m src.load.upload_gcs --layer all
```

Opções disponíveis:

| Opção            | Descrição                    |
| ---------------- | ---------------------------- |
| `--layer bronze` | Envia apenas a camada Bronze |
| `--layer silver` | Envia apenas a camada Silver |
| `--layer all`    | Envia Bronze e Silver        |

---

### Carga no BigQuery

```bash
python -m src.load.load_bigquery --table all --ano 2026 --mes 3
```

Opções disponíveis:

| Opção               | Descrição                            |
| ------------------- | ------------------------------------ |
| `--table deputados` | Carrega apenas a tabela de deputados |
| `--table despesas`  | Carrega apenas a tabela de despesas  |
| `--table all`       | Carrega deputados e despesas         |

---

### Criação da camada Gold

```bash
python -m src.load.run_bigquery_sql --target all
```

Opções disponíveis:

| Opção             | Descrição                    |
| ----------------- | ---------------------------- |
| `--target tables` | Cria apenas tabelas Gold     |
| `--target views`  | Cria apenas views analíticas |
| `--target all`    | Cria tabelas Gold e views    |

---

## Execução com Apache Airflow

O Airflow é executado localmente com Docker Compose.

---

### 1. Subir os containers

```bash
docker compose --env-file .env.airflow up -d
```

Serviços esperados:

```text
postgres
airflow-webserver
airflow-scheduler
```

---

### 2. Acessar a interface do Airflow

Acesse no navegador:

```text
http://localhost:8080
```

Credenciais locais:

```text
Usuário: admin
Senha: admin
```

---

### 3. Executar a DAG

Na interface do Airflow, localize a DAG:

```text
camara_deputados_etl_dag
```

Ative a DAG e execute manualmente.

---

### 4. Fluxo da DAG

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

---

### 5. Parar os containers

```bash
docker compose --env-file .env.airflow down
```

---

## Permissões locais para Airflow

Como o Airflow roda em container, pode ser necessário ajustar permissões dos diretórios montados.

### Permissões para dados, logs e DAGs

```bash
sudo chown -R 50000:0 data logs plugins config dags
sudo chmod -R 775 data logs plugins config dags
```

### Permissões para credenciais

```bash
sudo chown -R $USER:root credentials
sudo chmod 750 credentials
sudo chmod 640 credentials/*.json
```

Essas permissões permitem que:

* o Airflow escreva nos diretórios montados;
* o Airflow leia a credencial da Service Account;
* o usuário local continue acessando a pasta `credentials`.

---

## Validação no Google Cloud Storage

Para listar os arquivos enviados ao bucket:

```bash
gcloud storage ls --recursive gs://etl-camara-deputados-luis-2026-data-lake
```

Estrutura esperada:

```text
gs://etl-camara-deputados-luis-2026-data-lake/bronze/
gs://etl-camara-deputados-luis-2026-data-lake/silver/
gs://etl-camara-deputados-luis-2026-data-lake/gold/
```

---

## Validação no BigQuery

### Listar tabelas e views

```bash
bq ls etl-camara-deputados-luis-2026:camara_analytics
```

Tabelas esperadas:

```text
deputados
despesas
dim_deputado
dim_partido
dim_fornecedor
dim_tipo_despesa
fato_despesas
vw_kpis_gerais
vw_ranking_deputados
vw_ranking_partidos
vw_ranking_ufs
vw_ranking_fornecedores
vw_ranking_tipos_despesa
vw_evolucao_mensal
```

---

### Consultar KPIs gerais

```bash
bq query --use_legacy_sql=false \
'SELECT * FROM `etl-camara-deputados-luis-2026.camara_analytics.vw_kpis_gerais`'
```

---

### Validar quantidade de deputados

```bash
bq query --use_legacy_sql=false \
'SELECT COUNT(*) AS total FROM `etl-camara-deputados-luis-2026.camara_analytics.deputados`'
```

---

### Validar quantidade de despesas

```bash
bq query --use_legacy_sql=false \
'SELECT COUNT(*) AS total FROM `etl-camara-deputados-luis-2026.camara_analytics.despesas`'
```

---

## Comandos úteis

### Ver containers ativos

```bash
docker ps
```

---

### Ver status dos serviços do Docker Compose

```bash
docker compose --env-file .env.airflow ps
```

---

### Ver logs do scheduler

```bash
docker compose --env-file .env.airflow logs -f airflow-scheduler
```

---

### Ver logs do webserver

```bash
docker compose --env-file .env.airflow logs -f airflow-webserver
```

---

### Recriar ambiente Airflow do zero

```bash
docker compose --env-file .env.airflow down -v
docker compose --env-file .env.airflow build
docker compose --env-file .env.airflow up airflow-init
docker compose --env-file .env.airflow up -d
```

---

## Troubleshooting

### Erro: UID not found

Sintoma:

```text
getpwuid(): uid not found
```

Solução:

No arquivo `.env.airflow`, use:

```env
AIRFLOW_UID=50000
```

Depois reinicie os containers.

---

### Erro: permission denied em `data/`

Sintoma:

```text
PermissionError: [Errno 13] Permission denied
```

Solução:

```bash
sudo chown -R 50000:0 data logs plugins config dags
sudo chmod -R 775 data logs plugins config dags
```

---

### Erro: permission denied em `credentials/`

Sintoma:

```text
PermissionError: [Errno 13] Permission denied: 'credentials/etl-camara-sa.json'
```

Solução:

```bash
sudo chown -R $USER:root credentials
sudo chmod 750 credentials
sudo chmod 640 credentials/*.json
```

---

### Erro de autenticação GCP

Verifique se o `.env` possui:

```env
GOOGLE_APPLICATION_CREDENTIALS=credentials/sua-service-account.json
```

E confirme se a chave existe:

```bash
ls -la credentials
```

---

### Erro ao conectar no Docker dentro do WSL

Verifique se o Docker Desktop está aberto no Windows e se a integração com WSL está habilitada.

Comandos de validação:

```bash
docker --version
docker compose version
docker ps
```

---

## Encerramento dos recursos

Para evitar execução local desnecessária:

```bash
docker compose --env-file .env.airflow down
```

Para verificar recursos cloud:

```bash
gcloud storage buckets list
bq ls etl-camara-deputados-luis-2026:camara_analytics
```

---

## Observações finais

* O arquivo `.env` não deve ser enviado ao GitHub.
* A pasta `credentials/` não deve ser enviada ao GitHub.
* A chave da Service Account deve permanecer apenas localmente.
* O Airflow utilizado neste projeto é local via Docker, não Cloud Composer.
* O bucket GCS foi configurado com versionamento e soft delete desativados para reduzir risco de custo.

```
```
