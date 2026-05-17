-- Total geral de despesas no período
SELECT
  SUM(valor_liquido) AS total_valor_liquido
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas`;

-- Ranking de deputados por valor líquido
SELECT
  d.nome_deputado,
  d.sigla_partido,
  d.sigla_uf,
  SUM(f.valor_liquido) AS total_valor_liquido,
  COUNT(*) AS quantidade_despesas
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas` f
LEFT JOIN `etl-camara-deputados-luis-2026.camara_analytics.dim_deputado` d
  ON f.id_deputado = d.id_deputado
GROUP BY
  d.nome_deputado,
  d.sigla_partido,
  d.sigla_uf
ORDER BY total_valor_liquido DESC;

-- Ranking por tipo de despesa
SELECT
  tipo_despesa,
  SUM(valor_liquido) AS total_valor_liquido,
  COUNT(*) AS quantidade_despesas
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas`
GROUP BY tipo_despesa
ORDER BY total_valor_liquido DESC;

-- Ranking por fornecedor
SELECT
  nome_fornecedor,
  cnpj_cpf_fornecedor,
  SUM(valor_liquido) AS total_valor_liquido,
  COUNT(*) AS quantidade_despesas
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas`
GROUP BY
  nome_fornecedor,
  cnpj_cpf_fornecedor
ORDER BY total_valor_liquido DESC;

-- Evolução mensal
SELECT
  ano,
  mes,
  SUM(valor_liquido) AS total_valor_liquido,
  COUNT(*) AS quantidade_despesas
FROM `etl-camara-deputados-luis-2026.camara_analytics.fato_despesas`
GROUP BY ano, mes
ORDER BY ano, mes;
