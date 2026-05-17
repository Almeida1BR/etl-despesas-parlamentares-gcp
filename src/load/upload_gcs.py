import argparse
from pathlib import Path

from google.cloud import storage

from src.utils.config import GCP_BUCKET_NAME, GOOGLE_APPLICATION_CREDENTIALS
from src.utils.logger import get_logger
from src.utils.paths import BRONZE_DIR, SILVER_DIR


logger = get_logger(__name__)


def get_storage_client() -> storage.Client:
    if GOOGLE_APPLICATION_CREDENTIALS:
        return storage.Client.from_service_account_json(
            GOOGLE_APPLICATION_CREDENTIALS
        )

    return storage.Client()


def upload_file_to_gcs(
    bucket_name: str,
    local_path: Path,
    destination_blob_name: str,
) -> None:
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(str(local_path))

    logger.info(
        "Arquivo enviado para GCS | local=%s | gcs=gs://%s/%s",
        local_path,
        bucket_name,
        destination_blob_name,
    )


def upload_directory_to_gcs(
    local_dir: Path,
    bucket_name: str,
    gcs_prefix: str,
) -> None:
    if not local_dir.exists():
        raise FileNotFoundError(f"Diretório local não encontrado: {local_dir}")

    files = [file for file in local_dir.rglob("*") if file.is_file()]

    if not files:
        logger.warning("Nenhum arquivo encontrado em: %s", local_dir)
        return

    logger.info(
        "Iniciando upload de diretório | local=%s | destino=gs://%s/%s | arquivos=%s",
        local_dir,
        bucket_name,
        gcs_prefix,
        len(files),
    )

    for file_path in files:
        relative_path = file_path.relative_to(local_dir)
        destination_blob_name = f"{gcs_prefix}/{relative_path}".replace("\\", "/")

        upload_file_to_gcs(
            bucket_name=bucket_name,
            local_path=file_path,
            destination_blob_name=destination_blob_name,
        )

    logger.info("Upload concluído | diretório=%s | arquivos=%s", local_dir, len(files))


def upload_bronze() -> None:
    upload_directory_to_gcs(
        local_dir=BRONZE_DIR,
        bucket_name=GCP_BUCKET_NAME,
        gcs_prefix="bronze",
    )


def upload_silver() -> None:
    upload_directory_to_gcs(
        local_dir=SILVER_DIR,
        bucket_name=GCP_BUCKET_NAME,
        gcs_prefix="silver",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Faz upload das camadas Bronze e Silver locais para o Google Cloud Storage."
    )

    parser.add_argument(
        "--layer",
        choices=["bronze", "silver", "all"],
        default="all",
        help="Camada a ser enviada para o GCS.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not GCP_BUCKET_NAME:
        raise ValueError("Variável GCP_BUCKET_NAME não configurada no .env")

    logger.info("Bucket GCS configurado: %s", GCP_BUCKET_NAME)

    if args.layer in ["bronze", "all"]:
        upload_bronze()

    if args.layer in ["silver", "all"]:
        upload_silver()

    logger.info("Processo de upload para GCS finalizado")


if __name__ == "__main__":
    main()
