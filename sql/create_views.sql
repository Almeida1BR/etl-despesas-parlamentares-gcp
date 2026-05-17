CREATE OR REPLACE VIEW `etl-camara-deputados-luis-2026.camara_analytics.vw_kpis_gerais` AS
SELECT
  COUNT(*) AS quantidade_despesas,
  COUNT(DISTINCT id_deputado) AS quantidade_deputados,
  COUNT(DISTINCT cnpj_cpf_fornecedor) AS quantidade_fornecedores,
  COUNT(DISTINCT tipo_despesa) AS quantidade_tipos_despesa,
  SUM(valor_documento) AS total_valor_documento,
  SUM(valor_liquido) AS total_valor_liquido,
  SUM(valor_glosa) AS total_valor_glosa,
  AVG(valor_liquido) AS media_valor_liquido
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas`;

CREATE OR REPLACE VIEW `etl-camara-deputados-luis-2026.camara_analytics.vw_ranking_deputados` AS
SELECT
  d.id_deputado,
  d.nome_deputado,
  d.sigla_partido,
  d.sigla_uf,
  SUM(f.valor_liquido) AS total_valor_liquido,
  COUNT(*) AS quantidade_despesas,
  AVG(f.valor_liquido) AS media_valor_liquido
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas` f
LEFT JOIN `etl-camara-deputados-luis-2026.camara_analytics.dim_deputado` d
  ON f.id_deputado = d.id_deputado
GROUP BY
  d.id_deputado,
  d.nome_deputado,
  d.sigla_partido,
  d.sigla_uf;

CREATE OR REPLACE VIEW `etl-camara-deputados-luis-2026.camara_analytics.vw_ranking_partidos` AS
SELECT
  d.sigla_partido,
  SUM(f.valor_liquido) AS total_valor_liquido,
  COUNT(*) AS quantidade_despesas,
  COUNT(DISTINCT f.id_deputado) AS quantidade_deputados
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas` f
LEFT JOIN `etl-camara-deputados-luis-2026.camara_analytics.dim_deputado` d
  ON f.id_deputado = d.id_deputado
GROUP BY d.sigla_partido;

CREATE OR REPLACE VIEW `etl-camara-deputados-luis-2026.camara_analytics.vw_ranking_ufs` AS
SELECT
  d.sigla_uf,
  SUM(f.valor_liquido) AS total_valor_liquido,
  COUNT(*) AS quantidade_despesas,
  COUNT(DISTINCT f.id_deputado) AS quantidade_deputados
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas` f
LEFT JOIN `etl-camara-deputados-luis-2026.camara_analytics.dim_deputado` d
  ON f.id_deputado = d.id_deputado
GROUP BY d.sigla_uf;

CREATE OR REPLACE VIEW `etl-camara-deputados-luis-2026.camara_analytics.vw_ranking_fornecedores` AS
SELECT
  nome_fornecedor,
  cnpj_cpf_fornecedor,
  SUM(valor_liquido) AS total_valor_liquido,
  COUNT(*) AS quantidade_despesas,
  COUNT(DISTINCT id_deputado) AS quantidade_deputados
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas`
GROUP BY
  nome_fornecedor,
  cnpj_cpf_fornecedor;

CREATE OR REPLACE VIEW `etl-camara-deputados-luis-2026.camara_analytics.vw_ranking_tipos_despesa` AS
SELECT
  tipo_despesa,
  SUM(valor_liquido) AS total_valor_liquido,
  COUNT(*) AS quantidade_despesas,
  AVG(valor_liquido) AS media_valor_liquido
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas`
GROUP BY tipo_despesa;

CREATE OR REPLACE VIEW `etl-camara-deputados-luis-2026.camara_analytics.vw_evolucao_mensal` AS
SELECT
  ano,
  mes,
  DATE(ano, mes, 1) AS data_referencia,
  SUM(valor_liquido) AS total_valor_liquido,
  COUNT(*) AS quantidade_despesas,
  COUNT(DISTINCT id_deputado) AS quantidade_deputados
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas`
GROUP BY
  ano,
  mes,
  data_referencia;
