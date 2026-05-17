import argparse
from pathlib import Path

import pandas as pd

from src.utils.config import DEFAULT_MONTH, DEFAULT_YEAR
from src.utils.logger import get_logger
from src.utils.paths import SILVER_DIR


logger = get_logger(__name__)


def validate_file_exists(file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    logger.info("Arquivo encontrado: %s", file_path)


def validate_not_empty(df: pd.DataFrame, table_name: str) -> None:
    if df.empty:
        raise ValueError(f"Tabela {table_name} está vazia")

    logger.info("Tabela %s não está vazia. Linhas: %s", table_name, len(df))


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    table_name: str,
) -> None:
    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Tabela {table_name} está sem colunas obrigatórias: {missing_columns}"
        )

    logger.info("Tabela %s contém todas as colunas obrigatórias", table_name)


def validate_not_null(
    df: pd.DataFrame,
    columns: list[str],
    table_name: str,
) -> None:
    for column in columns:
        null_count = df[column].isna().sum()

        if null_count > 0:
            raise ValueError(
                f"Tabela {table_name}: coluna {column} possui {null_count} valores nulos"
            )

    logger.info("Tabela %s não possui nulos nas colunas críticas", table_name)


def validate_year_month(
    df: pd.DataFrame,
    ano: int,
    mes: int,
    table_name: str,
) -> None:
    if "ano" in df.columns:
        invalid_year = df[df["ano"] != ano]

        if not invalid_year.empty:
            raise ValueError(
                f"Tabela {table_name}: existem registros com ano diferente de {ano}"
            )

    if "mes" in df.columns:
        invalid_month = df[df["mes"] != mes]

        if not invalid_month.empty:
            raise ValueError(
                f"Tabela {table_name}: existem registros com mês diferente de {mes}"
            )

    logger.info("Tabela %s possui ano/mês coerentes", table_name)


def validate_numeric_non_negative(
    df: pd.DataFrame,
    columns: list[str],
    table_name: str,
) -> None:
    for column in columns:
        invalid_values = df[df[column].isna()]

        if not invalid_values.empty:
            raise ValueError(
                f"Tabela {table_name}: coluna {column} possui valores não numéricos/nulos"
            )

        negative_values = df[df[column] < 0]

        if not negative_values.empty:
            logger.warning(
                "Tabela %s: coluna %s possui %s valores negativos",
                table_name,
                column,
                len(negative_values),
            )

    logger.info("Tabela %s possui valores monetários numéricos", table_name)


def validate_no_duplicates(
    df: pd.DataFrame,
    subset: list[str],
    table_name: str,
) -> None:
    duplicated_count = df.duplicated(subset=subset).sum()

    if duplicated_count > 0:
        raise ValueError(
            f"Tabela {table_name}: existem {duplicated_count} duplicidades técnicas"
        )

    logger.info("Tabela %s não possui duplicidades técnicas", table_name)


def run_deputados_checks() -> None:
    file_path = SILVER_DIR / "deputados" / "deputados.parquet"

    validate_file_exists(file_path)

    df = pd.read_parquet(file_path)

    table_name = "deputados"

    required_columns = [
        "id_deputado",
        "nome_deputado",
        "sigla_partido",
        "sigla_uf",
        "id_legislatura",
        "data_carga",
    ]

    validate_not_empty(df, table_name)
    validate_required_columns(df, required_columns, table_name)
    validate_not_null(df, ["id_deputado", "nome_deputado"], table_name)
    validate_no_duplicates(df, ["id_deputado"], table_name)

    logger.info("Quality checks de deputados concluídos com sucesso")


def run_despesas_checks(ano: int, mes: int) -> None:
    file_path = (
        SILVER_DIR
        / "despesas"
        / f"ano={ano}"
        / f"mes={mes:02d}"
        / "despesas.parquet"
    )

    validate_file_exists(file_path)

    df = pd.read_parquet(file_path)

    table_name = "despesas"

    required_columns = [
        "id_deputado",
        "ano",
        "mes",
        "tipo_despesa",
        "cod_documento",
        "data_documento",
        "nome_fornecedor",
        "cnpj_cpf_fornecedor",
        "valor_documento",
        "valor_liquido",
        "valor_glosa",
        "cod_lote",
        "parcela",
        "ano_referencia",
        "mes_referencia",
        "data_carga",
    ]

    validate_not_empty(df, table_name)
    validate_required_columns(df, required_columns, table_name)
    validate_not_null(df, ["id_deputado", "ano", "mes", "tipo_despesa"], table_name)
    validate_year_month(df, ano, mes, table_name)
    validate_numeric_non_negative(
        df,
        ["valor_documento", "valor_liquido", "valor_glosa"],
        table_name,
    )
    validate_no_duplicates(
        df,
        [
            "id_deputado",
            "ano",
            "mes",
            "cod_documento",
            "cod_lote",
            "parcela",
        ],
        table_name,
    )

    logger.info("Quality checks de despesas concluídos com sucesso")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa quality checks nos arquivos Silver locais."
    )

    parser.add_argument(
        "--ano",
        type=int,
        default=DEFAULT_YEAR,
        help="Ano de referência das despesas.",
    )

    parser.add_argument(
        "--mes",
        type=int,
        default=DEFAULT_MONTH,
        help="Mês de referência das despesas.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logger.info("Iniciando quality checks locais")
    logger.info("Ano/mês de referência: %s/%s", args.ano, f"{args.mes:02d}")

    run_deputados_checks()
    run_despesas_checks(ano=args.ano, mes=args.mes)

    logger.info("Todos os quality checks foram concluídos com sucesso")


if __name__ == "__main__":
    main()
