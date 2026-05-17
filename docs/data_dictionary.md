````markdown
# Dicionário de Dados

Este documento descreve as principais tabelas e views analíticas criadas no BigQuery para o projeto de despesas parlamentares.

O objetivo do dicionário de dados é documentar a estrutura lógica das tabelas, o significado dos campos e o papel de cada entidade dentro da camada analítica.

---

## Visão geral das tabelas

O projeto possui dois grupos principais de tabelas no BigQuery:

1. **Tabelas staging**, carregadas a partir da camada Silver.
2. **Tabelas Gold**, modeladas para análise.

---

## Tabelas staging

As tabelas staging recebem diretamente os arquivos Parquet tratados da camada Silver.

```text
deputados
despesas
````

Essas tabelas servem como base para criação das dimensões, tabela fato e views analíticas.

---

# Tabela: deputados

Tabela carregada a partir do arquivo:

```text
data/processed/silver/deputados/deputados.parquet
```

No BigQuery:

```text
camara_analytics.deputados
```

## Descrição

Contém informações cadastrais dos deputados federais retornados pelo endpoint `/deputados` da API Dados Abertos da Câmara.

## Colunas

| Coluna           | Tipo lógico | Descrição                                                |
| ---------------- | ----------- | -------------------------------------------------------- |
| `id_deputado`    | Inteiro     | Identificador único do deputado na API da Câmara         |
| `uri_deputado`   | Texto       | URI do recurso do deputado na API                        |
| `nome_deputado`  | Texto       | Nome parlamentar do deputado                             |
| `sigla_partido`  | Texto       | Sigla do partido político do deputado                    |
| `uri_partido`    | Texto       | URI do recurso do partido na API                         |
| `sigla_uf`       | Texto       | Unidade federativa de representação do deputado          |
| `id_legislatura` | Inteiro     | Identificador da legislatura                             |
| `url_foto`       | Texto       | URL da foto oficial do deputado                          |
| `email`          | Texto       | E-mail institucional informado pela API                  |
| `data_carga`     | Timestamp   | Data e hora em que o registro foi processado na pipeline |

## Observações

* A tabela possui um registro por deputado.
* A chave principal lógica é `id_deputado`.
* Essa tabela é usada como base para a dimensão `dim_deputado`.

---

# Tabela: despesas

Tabela carregada a partir do arquivo:

```text
data/processed/silver/despesas/ano=2026/mes=03/despesas.parquet
```

No BigQuery:

```text
camara_analytics.despesas
```

## Descrição

Contém os registros tratados de despesas parlamentares retornados pelo endpoint `/deputados/{id}/despesas`.

## Colunas

| Coluna                | Tipo lógico | Descrição                                                |
| --------------------- | ----------- | -------------------------------------------------------- |
| `id_deputado`         | Inteiro     | Identificador do deputado associado à despesa            |
| `ano`                 | Inteiro     | Ano da despesa conforme retornado pela API               |
| `mes`                 | Inteiro     | Mês da despesa conforme retornado pela API               |
| `tipo_despesa`        | Texto       | Categoria da despesa parlamentar                         |
| `cod_documento`       | Inteiro     | Código do documento fiscal                               |
| `tipo_documento`      | Texto       | Tipo do documento fiscal                                 |
| `cod_tipo_documento`  | Inteiro     | Código do tipo de documento                              |
| `data_documento`      | Data        | Data de emissão do documento                             |
| `num_documento`       | Texto       | Número do documento fiscal                               |
| `valor_documento`     | Numérico    | Valor bruto do documento                                 |
| `url_documento`       | Texto       | URL do documento fiscal, quando disponível               |
| `nome_fornecedor`     | Texto       | Nome do fornecedor da despesa                            |
| `cnpj_cpf_fornecedor` | Texto       | CNPJ ou CPF do fornecedor                                |
| `valor_liquido`       | Numérico    | Valor líquido considerado para a despesa                 |
| `valor_glosa`         | Numérico    | Valor glosado                                            |
| `num_ressarcimento`   | Texto       | Número de ressarcimento, quando disponível               |
| `cod_lote`            | Inteiro     | Código do lote da despesa                                |
| `parcela`             | Inteiro     | Número da parcela                                        |
| `ano_referencia`      | Inteiro     | Ano utilizado como parâmetro da pipeline                 |
| `mes_referencia`      | Inteiro     | Mês utilizado como parâmetro da pipeline                 |
| `data_carga`          | Timestamp   | Data e hora em que o registro foi processado na pipeline |

## Observações

* Essa tabela representa a base transacional de despesas.
* A chave técnica de deduplicação considera deputado, ano, mês, documento, lote e parcela.
* Alguns campos, como `cod_documento` e `url_documento`, podem apresentar valores nulos dependendo do retorno da API.
* Valores negativos em `valor_documento` ou `valor_liquido` são preservados, pois podem representar estornos, ajustes ou devoluções.

---

# Camada Gold

A camada Gold é composta por dimensões, tabela fato e views analíticas criadas no BigQuery.

---

# Tabela: dim_deputado

No BigQuery:

```text
camara_analytics.dim_deputado
```

## Descrição

Dimensão com informações cadastrais dos deputados.

## Origem

```text
camara_analytics.deputados
```

## Colunas

| Coluna           | Tipo lógico | Descrição                       |
| ---------------- | ----------- | ------------------------------- |
| `id_deputado`    | Inteiro     | Identificador único do deputado |
| `nome_deputado`  | Texto       | Nome parlamentar do deputado    |
| `sigla_partido`  | Texto       | Sigla do partido político       |
| `sigla_uf`       | Texto       | Unidade federativa              |
| `id_legislatura` | Inteiro     | Identificador da legislatura    |
| `uri_deputado`   | Texto       | URI do deputado na API          |
| `uri_partido`    | Texto       | URI do partido na API           |
| `url_foto`       | Texto       | URL da foto oficial             |
| `email`          | Texto       | E-mail institucional            |
| `data_carga`     | Timestamp   | Data e hora da carga            |

## Chave lógica

```text
id_deputado
```

---

# Tabela: dim_partido

No BigQuery:

```text
camara_analytics.dim_partido
```

## Descrição

Dimensão simples de partidos políticos.

## Origem

```text
camara_analytics.deputados
```

## Colunas

| Coluna          | Tipo lógico | Descrição                 |
| --------------- | ----------- | ------------------------- |
| `sigla_partido` | Texto       | Sigla do partido político |

## Observações

* A dimensão é derivada dos partidos encontrados nos registros de deputados.
* Pode ser expandida futuramente com dados adicionais de partidos.

---

# Tabela: dim_fornecedor

No BigQuery:

```text
camara_analytics.dim_fornecedor
```

## Descrição

Dimensão de fornecedores presentes nas despesas parlamentares.

## Origem

```text
camara_analytics.despesas
```

## Colunas

| Coluna                | Tipo lógico | Descrição               |
| --------------------- | ----------- | ----------------------- |
| `cnpj_cpf_fornecedor` | Texto       | Documento do fornecedor |
| `nome_fornecedor`     | Texto       | Nome do fornecedor      |

## Chave lógica

```text
cnpj_cpf_fornecedor
```

## Observações

* A identificação do fornecedor depende da qualidade do campo retornado pela API.
* O mesmo fornecedor pode aparecer com pequenas variações de nome em bases públicas.

---

# Tabela: dim_tipo_despesa

No BigQuery:

```text
camara_analytics.dim_tipo_despesa
```

## Descrição

Dimensão com as categorias de despesas parlamentares.

## Origem

```text
camara_analytics.despesas
```

## Colunas

| Coluna         | Tipo lógico | Descrição                        |
| -------------- | ----------- | -------------------------------- |
| `tipo_despesa` | Texto       | Categoria da despesa parlamentar |

## Observações

* A dimensão permite análises por natureza da despesa.
* Exemplos de categorias podem incluir divulgação da atividade parlamentar, combustíveis, passagens, hospedagens e outros tipos retornados pela API.

---

# Tabela: fato_despesas

No BigQuery:

```text
camara_analytics.fato_despesas
```

## Descrição

Tabela fato com os eventos financeiros de despesas parlamentares.

## Origem

```text
camara_analytics.despesas
```

## Colunas

| Coluna                | Tipo lógico | Descrição                                  |
| --------------------- | ----------- | ------------------------------------------ |
| `id_deputado`         | Inteiro     | Chave de relacionamento com `dim_deputado` |
| `ano`                 | Inteiro     | Ano da despesa                             |
| `mes`                 | Inteiro     | Mês da despesa                             |
| `ano_referencia`      | Inteiro     | Ano parametrizado na execução da pipeline  |
| `mes_referencia`      | Inteiro     | Mês parametrizado na execução da pipeline  |
| `tipo_despesa`        | Texto       | Categoria da despesa                       |
| `cod_documento`       | Inteiro     | Código do documento fiscal                 |
| `tipo_documento`      | Texto       | Tipo do documento                          |
| `cod_tipo_documento`  | Inteiro     | Código do tipo de documento                |
| `data_documento`      | Data        | Data do documento fiscal                   |
| `num_documento`       | Texto       | Número do documento                        |
| `valor_documento`     | Numérico    | Valor bruto do documento                   |
| `valor_liquido`       | Numérico    | Valor líquido considerado                  |
| `valor_glosa`         | Numérico    | Valor glosado                              |
| `num_ressarcimento`   | Texto       | Número de ressarcimento                    |
| `cod_lote`            | Inteiro     | Código do lote                             |
| `parcela`             | Inteiro     | Parcela do documento                       |
| `nome_fornecedor`     | Texto       | Nome do fornecedor                         |
| `cnpj_cpf_fornecedor` | Texto       | Documento do fornecedor                    |
| `url_documento`       | Texto       | URL do documento                           |
| `data_carga`          | Timestamp   | Data e hora da carga                       |

## Métricas principais

| Métrica             | Campo base             |
| ------------------- | ---------------------- |
| Total de despesas   | `COUNT(*)`             |
| Valor bruto total   | `SUM(valor_documento)` |
| Valor líquido total | `SUM(valor_liquido)`   |
| Valor glosado total | `SUM(valor_glosa)`     |
| Média por despesa   | `AVG(valor_liquido)`   |

## Dimensões relacionadas

| Dimensão           | Chave de relacionamento          |
| ------------------ | -------------------------------- |
| `dim_deputado`     | `id_deputado`                    |
| `dim_fornecedor`   | `cnpj_cpf_fornecedor`            |
| `dim_tipo_despesa` | `tipo_despesa`                   |
| `dim_partido`      | via `dim_deputado.sigla_partido` |

---

# Views analíticas

As views analíticas foram criadas para facilitar consultas exploratórias e construção de dashboards.

---

## View: vw_kpis_gerais

No BigQuery:

```text
camara_analytics.vw_kpis_gerais
```

## Descrição

View com indicadores consolidados do período processado.

## Campos

| Campo                      | Descrição                                       |
| -------------------------- | ----------------------------------------------- |
| `quantidade_despesas`      | Quantidade total de registros de despesa        |
| `quantidade_deputados`     | Quantidade de deputados com despesas no recorte |
| `quantidade_fornecedores`  | Quantidade de fornecedores distintos            |
| `quantidade_tipos_despesa` | Quantidade de categorias de despesa             |
| `total_valor_documento`    | Soma dos valores brutos                         |
| `total_valor_liquido`      | Soma dos valores líquidos                       |
| `total_valor_glosa`        | Soma dos valores glosados                       |
| `media_valor_liquido`      | Média do valor líquido das despesas             |

---

## View: vw_ranking_deputados

No BigQuery:

```text
camara_analytics.vw_ranking_deputados
```

## Descrição

Ranking de deputados por valor líquido total de despesas.

## Campos principais

| Campo                 | Descrição                 |
| --------------------- | ------------------------- |
| `id_deputado`         | Identificador do deputado |
| `nome_deputado`       | Nome parlamentar          |
| `sigla_partido`       | Partido do deputado       |
| `sigla_uf`            | Unidade federativa        |
| `total_valor_liquido` | Soma do valor líquido     |
| `quantidade_despesas` | Quantidade de despesas    |
| `media_valor_liquido` | Média do valor líquido    |

---

## View: vw_ranking_partidos

No BigQuery:

```text
camara_analytics.vw_ranking_partidos
```

## Descrição

Ranking de partidos por valor líquido total de despesas.

## Campos principais

| Campo                  | Descrição                         |
| ---------------------- | --------------------------------- |
| `sigla_partido`        | Sigla do partido                  |
| `total_valor_liquido`  | Soma do valor líquido             |
| `quantidade_despesas`  | Quantidade de despesas            |
| `quantidade_deputados` | Quantidade de deputados distintos |

---

## View: vw_ranking_ufs

No BigQuery:

```text
camara_analytics.vw_ranking_ufs
```

## Descrição

Ranking de unidades federativas por valor líquido total de despesas.

## Campos principais

| Campo                  | Descrição                         |
| ---------------------- | --------------------------------- |
| `sigla_uf`             | Unidade federativa                |
| `total_valor_liquido`  | Soma do valor líquido             |
| `quantidade_despesas`  | Quantidade de despesas            |
| `quantidade_deputados` | Quantidade de deputados distintos |

---

## View: vw_ranking_fornecedores

No BigQuery:

```text
camara_analytics.vw_ranking_fornecedores
```

## Descrição

Ranking de fornecedores por valor líquido total de despesas.

## Campos principais

| Campo                  | Descrição                         |
| ---------------------- | --------------------------------- |
| `nome_fornecedor`      | Nome do fornecedor                |
| `cnpj_cpf_fornecedor`  | Documento do fornecedor           |
| `total_valor_liquido`  | Soma do valor líquido             |
| `quantidade_despesas`  | Quantidade de despesas            |
| `quantidade_deputados` | Quantidade de deputados distintos |

---

## View: vw_ranking_tipos_despesa

No BigQuery:

```text
camara_analytics.vw_ranking_tipos_despesa
```

## Descrição

Ranking por categoria de despesa.

## Campos principais

| Campo                 | Descrição              |
| --------------------- | ---------------------- |
| `tipo_despesa`        | Categoria da despesa   |
| `total_valor_liquido` | Soma do valor líquido  |
| `quantidade_despesas` | Quantidade de despesas |
| `media_valor_liquido` | Média do valor líquido |

---

## View: vw_evolucao_mensal

No BigQuery:

```text
camara_analytics.vw_evolucao_mensal
```

## Descrição

View para análise temporal mensal das despesas.

## Campos principais

| Campo                  | Descrição                                          |
| ---------------------- | -------------------------------------------------- |
| `ano`                  | Ano da despesa                                     |
| `mes`                  | Mês da despesa                                     |
| `data_referencia`      | Data sintética representando o primeiro dia do mês |
| `total_valor_liquido`  | Soma do valor líquido                              |
| `quantidade_despesas`  | Quantidade de despesas                             |
| `quantidade_deputados` | Quantidade de deputados distintos                  |

---

# Regras de qualidade consideradas

## Campos críticos

Campos que não devem ser nulos:

```text
id_deputado
ano
mes
tipo_despesa
nome_deputado
```

## Deduplicação técnica

A deduplicação de despesas considera:

```text
id_deputado
ano
mes
cod_documento
cod_lote
parcela
```

## Valores negativos

Valores negativos em campos monetários são mantidos como warning, não erro.

Motivo: podem representar ajustes, estornos, correções ou devoluções.

---

# Resultado validado no MVP

No recorte inicial processado:

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

```
```
