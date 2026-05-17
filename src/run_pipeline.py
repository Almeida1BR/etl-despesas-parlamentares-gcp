import argparse

from src.extract.extract_deputados import extract_deputados, save_deputados_raw
from src.extract.extract_despesas import extract_despesas_periodo, save_despesas_raw
from src.load.load_bigquery import load_deputados, load_despesas
from src.load.run_bigquery_sql import run_analytical_views, run_gold_tables
from src.load.upload_gcs import upload_bronze, upload_silver
from src.quality.checks import run_deputados_checks, run_despesas_checks
from src.transform.transform_deputados import (
    get_latest_deputados_file,
    load_deputados_raw,
    save_deputados_silver,
    transform_deputados,
)
from src.transform.transform_despesas import (
    get_latest_despesas_file,
    load_despesas_raw,
    save_despesas_silver,
    transform_despesas,
)
from src.utils.config import DEFAULT_MONTH, DEFAULT_YEAR
from src.utils.logger import get_logger


logger = get_logger(__name__)


def run_extract(ano: int, mes: int, limite_deputados: int | None) -> None:
    logger.info("Iniciando etapa de extração")

    deputados = extract_deputados()
    save_deputados_raw(deputados)

    despesas = extract_despesas_periodo(
        ano=ano,
        mes=mes,
        limite_deputados=limite_deputados,
        deputados=deputados,
    )

    save_despesas_raw(
        despesas=despesas,
        ano=ano,
        mes=mes,
    )

    logger.info("Etapa de extração finalizada")


def run_transform(ano: int, mes: int) -> None:
    logger.info("Iniciando etapa de transformação")

    deputados_input_path = get_latest_deputados_file()
    deputados_raw = load_deputados_raw(deputados_input_path)

    df_deputados = transform_deputados(deputados_raw)
    save_deputados_silver(df_deputados)

    despesas_input_path = get_latest_despesas_file(
        ano=ano,
        mes=mes,
    )

    despesas_raw = load_despesas_raw(despesas_input_path)

    df_despesas = transform_despesas(
        data=despesas_raw,
        ano=ano,
        mes=mes,
    )

    save_despesas_silver(
        df=df_despesas,
        ano=ano,
        mes=mes,
    )

    logger.info("Etapa de transformação finalizada")


def run_quality(ano: int, mes: int) -> None:
    logger.info("Iniciando etapa de quality checks")

    run_deputados_checks()
    run_despesas_checks(
        ano=ano,
        mes=mes,
    )

    logger.info("Etapa de quality checks finalizada")


def run_cloud_load(ano: int, mes: int) -> None:
    logger.info("Iniciando etapa de upload para GCS")

    upload_bronze()
    upload_silver()

    logger.info("Upload para GCS finalizado")
    logger.info("Iniciando carga no BigQuery")

    load_deputados()
    load_despesas(
        ano=ano,
        mes=mes,
    )

    logger.info("Carga no BigQuery finalizada")


def run_gold() -> None:
    logger.info("Iniciando etapa Gold")

    run_gold_tables()
    run_analytical_views()

    logger.info("Etapa Gold finalizada")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa pipeline ETL completo de despesas parlamentares."
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

    parser.add_argument(
        "--limite-deputados",
        type=int,
        default=5,
        help="Quantidade máxima de deputados a processar. Use 0 para processar todos.",
    )

    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Pula etapa de extração.",
    )

    parser.add_argument(
        "--skip-transform",
        action="store_true",
        help="Pula etapa de transformação.",
    )

    parser.add_argument(
        "--skip-quality",
        action="store_true",
        help="Pula etapa de quality checks.",
    )

    parser.add_argument(
        "--skip-cloud-load",
        action="store_true",
        help="Pula upload para GCS e carga BigQuery.",
    )

    parser.add_argument(
        "--skip-gold",
        action="store_true",
        help="Pula criação de tabelas/views Gold.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    limite_deputados = (
        None if args.limite_deputados == 0 else args.limite_deputados
    )

    logger.info("Iniciando pipeline ETL")
    logger.info("Ano/mês: %s/%s", args.ano, f"{args.mes:02d}")
    logger.info("Limite de deputados: %s", limite_deputados)

    if not args.skip_extract:
        run_extract(
            ano=args.ano,
            mes=args.mes,
            limite_deputados=limite_deputados,
        )

    if not args.skip_transform:
        run_transform(
            ano=args.ano,
            mes=args.mes,
        )

    if not args.skip_quality:
        run_quality(
            ano=args.ano,
            mes=args.mes,
        )

    if not args.skip_cloud_load:
        run_cloud_load(
            ano=args.ano,
            mes=args.mes,
        )

    if not args.skip_gold:
        run_gold()

    logger.info("Pipeline ETL finalizado com sucesso")


if __name__ == "__main__":
    main()