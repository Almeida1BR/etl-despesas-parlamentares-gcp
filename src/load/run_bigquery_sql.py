import argparse
from pathlib import Path

from google.cloud import bigquery

from src.utils.config import GCP_PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS
from src.utils.logger import get_logger
from src.utils.paths import PROJECT_ROOT


logger = get_logger(__name__)


SQL_DIR = PROJECT_ROOT / "sql"


def get_bigquery_client() -> bigquery.Client:
    if GOOGLE_APPLICATION_CREDENTIALS:
        return bigquery.Client.from_service_account_json(
            GOOGLE_APPLICATION_CREDENTIALS,
            project=GCP_PROJECT_ID,
        )

    return bigquery.Client(project=GCP_PROJECT_ID)


def read_sql_file(sql_file_path: Path) -> str:
    if not sql_file_path.exists():
        raise FileNotFoundError(f"Arquivo SQL não encontrado: {sql_file_path}")

    logger.info("Lendo arquivo SQL: %s", sql_file_path)

    return sql_file_path.read_text(encoding="utf-8")


def execute_sql(sql: str, job_name: str) -> None:
    client = get_bigquery_client()

    logger.info("Iniciando execução SQL: %s", job_name)

    query_job = client.query(sql)
    query_job.result()

    logger.info("Execução SQL concluída: %s", job_name)


def run_sql_file(file_name: str) -> None:
    sql_file_path = SQL_DIR / file_name
    sql = read_sql_file(sql_file_path)

    execute_sql(
        sql=sql,
        job_name=file_name,
    )


def run_gold_tables() -> None:
    run_sql_file("create_tables.sql")


def run_analytical_views() -> None:
    run_sql_file("create_views.sql")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa scripts SQL no BigQuery para criação da camada Gold."
    )

    parser.add_argument(
        "--target",
        choices=["tables", "views", "all"],
        default="all",
        help="Define quais scripts SQL serão executados.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logger.info("Iniciando execução da camada Gold no BigQuery")
    logger.info("Target selecionado: %s", args.target)

    if args.target in ["tables", "all"]:
        run_gold_tables()

    if args.target in ["views", "all"]:
        run_analytical_views()

    logger.info("Execução da camada Gold finalizada")


if __name__ == "__main__":
    main()
