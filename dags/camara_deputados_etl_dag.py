from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


DEFAULT_ANO = 2026
DEFAULT_MES = 3
DEFAULT_LIMITE_DEPUTADOS = 5


with DAG(
    dag_id="camara_deputados_etl_dag",
    description="Pipeline ETL de despesas parlamentares com GCS e BigQuery",
    start_date=datetime(2026, 5, 1),
    schedule=None,
    catchup=False,
    tags=["engenharia-de-dados", "gcp", "bigquery", "camara"],
) as dag:

    extract = BashOperator(
        task_id="extract",
        bash_command=(
            "cd /opt/airflow && "
            "python -m src.run_pipeline "
            f"--ano {DEFAULT_ANO} "
            f"--mes {DEFAULT_MES} "
            f"--limite-deputados {DEFAULT_LIMITE_DEPUTADOS} "
            "--skip-transform "
            "--skip-quality "
            "--skip-cloud-load "
            "--skip-gold"
        ),
    )

    transform = BashOperator(
        task_id="transform",
        bash_command=(
            "cd /opt/airflow && "
            "python -m src.run_pipeline "
            f"--ano {DEFAULT_ANO} "
            f"--mes {DEFAULT_MES} "
            "--skip-extract "
            "--skip-quality "
            "--skip-cloud-load "
            "--skip-gold"
        ),
    )

    quality_checks = BashOperator(
        task_id="quality_checks",
        bash_command=(
            "cd /opt/airflow && "
            "python -m src.run_pipeline "
            f"--ano {DEFAULT_ANO} "
            f"--mes {DEFAULT_MES} "
            "--skip-extract "
            "--skip-transform "
            "--skip-cloud-load "
            "--skip-gold"
        ),
    )

    upload_gcs_and_load_bigquery = BashOperator(
        task_id="upload_gcs_and_load_bigquery",
        bash_command=(
            "cd /opt/airflow && "
            "python -m src.run_pipeline "
            f"--ano {DEFAULT_ANO} "
            f"--mes {DEFAULT_MES} "
            "--skip-extract "
            "--skip-transform "
            "--skip-quality "
            "--skip-gold"
        ),
    )

    run_gold_sql = BashOperator(
        task_id="run_gold_sql",
        bash_command=(
            "cd /opt/airflow && "
            "python -m src.run_pipeline "
            f"--ano {DEFAULT_ANO} "
            f"--mes {DEFAULT_MES} "
            "--skip-extract "
            "--skip-transform "
            "--skip-quality "
            "--skip-cloud-load"
        ),
    )

    extract >> transform >> quality_checks >> upload_gcs_and_load_bigquery >> run_gold_sql
