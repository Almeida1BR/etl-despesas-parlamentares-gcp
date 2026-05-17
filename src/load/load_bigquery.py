import argparse

from google.cloud import bigquery

from src.utils.config import (
    BIGQUERY_DATASET,
    GCP_BUCKET_NAME,
    GCP_PROJECT_ID,
    GOOGLE_APPLICATION_CREDENTIALS,
)
from src.utils.logger import get_logger


logger = get_logger(__name__)


def get_bigquery_client() -> bigquery.Client:
    if GOOGLE_APPLICATION_CREDENTIALS:
        return bigquery.Client.from_service_account_json(
            GOOGLE_APPLICATION_CREDENTIALS,
            project=GCP_PROJECT_ID,
        )

    return bigquery.Client(project=GCP_PROJECT_ID)


def load_parquet_from_gcs(
    source_uri: str,
    table_id: str,
    write_disposition: str = "WRITE_TRUNCATE",
) -> None:
    client = get_bigquery_client()

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=write_disposition,
        autodetect=True,
    )

    logger.info("Iniciando carga BigQuery | origem=%s | destino=%s", source_uri, table_id)

    load_job = client.load_table_from_uri(
        source_uri,
        table_id,
        job_config=job_config,
    )

    load_job.result()

    table = client.get_table(table_id)

    logger.info(
        "Carga concluída | tabela=%s | linhas=%s | colunas=%s",
        table_id,
        table.num_rows,
        len(table.schema),
    )


def load_deputados() -> None:
    source_uri = f"gs://{GCP_BUCKET_NAME}/silver/deputados/deputados.parquet"
    table_id = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.deputados"

    load_parquet_from_gcs(
        source_uri=source_uri,
        table_id=table_id,
    )


def load_despesas(ano: int, mes: int) -> None:
    source_uri = (
        f"gs://{GCP_BUCKET_NAME}/silver/despesas/"
        f"ano={ano}/mes={mes:02d}/despesas.parquet"
    )
    table_id = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.despesas"

    load_parquet_from_gcs(
        source_uri=source_uri,
        table_id=table_id,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Carrega arquivos Parquet do GCS para tabelas BigQuery."
    )

    parser.add_argument(
        "--table",
        choices=["deputados", "despesas", "all"],
        default="all",
        help="Tabela a ser carregada no BigQuery.",
    )

    parser.add_argument(
        "--ano",
        type=int,
        default=2026,
        help="Ano de referência para carga de despesas.",
    )

    parser.add_argument(
        "--mes",
        type=int,
        default=3,
        help="Mês de referência para carga de despesas.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.table in ["deputados", "all"]:
        load_deputados()

    if args.table in ["despesas", "all"]:
        load_despesas(ano=args.ano, mes=args.mes)

    logger.info("Processo de carga BigQuery finalizado")


if __name__ == "__main__":
    main()
