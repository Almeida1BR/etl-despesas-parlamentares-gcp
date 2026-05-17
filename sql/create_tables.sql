CREATE OR REPLACE TABLE `etl-camara-deputados-luis-2026.camara_analytics.dim_deputado` AS
SELECT DISTINCT
  id_deputado,
  nome_deputado,
  sigla_partido,
  sigla_uf,
  id_legislatura,
  uri_deputado,
  uri_partido,
  url_foto,
  email,
  data_carga
FROM `etl-camara-deputados-luis-2026.camara_analytics.deputados`;

CREATE OR REPLACE TABLE `etl-camara-deputados-luis-2026.camara_analytics.dim_partido` AS
SELECT DISTINCT
  sigla_partido
FROM `etl-camara-deputados-luis-2026.camara_analytics.deputados`
WHERE sigla_partido IS NOT NULL;

CREATE OR REPLACE TABLE `etl-camara-deputados-luis-2026.camara_analytics.dim_fornecedor` AS
SELECT DISTINCT
  cnpj_cpf_fornecedor,
  nome_fornecedor
FROM `etl-camara-deputados-luis-2026.camara_analytics.despesas`
WHERE cnpj_cpf_fornecedor IS NOT NULL
  AND nome_fornecedor IS NOT NULL;

CREATE OR REPLACE TABLE `etl-camara-deputados-luis-2026.camara_analytics.dim_tipo_despesa` AS
SELECT DISTINCT
  tipo_despesa
FROM `etl-camara-deputados-luis-2026.camara_analytics.despesas`
WHERE tipo_despesa IS NOT NULL;

CREATE OR REPLACE TABLE `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas` AS
SELECT
  id_deputado,
  ano,
  mes,
  ano_referencia,
  mes_referencia,
  tipo_despesa,
  cod_documento,
  tipo_documento,
  cod_tipo_documento,
  data_documento,
  num_documento,
  valor_documento,
  valor_liquido,
  valor_glosa,
  num_ressarcimento,
  cod_lote,
  parcela,
  nome_fornecedor,
  cnpj_cpf_fornecedor,
  url_documento,
  data_carga
FROM `etl-camara-deputados-luis-2026.camara_analytics.despesas`;
