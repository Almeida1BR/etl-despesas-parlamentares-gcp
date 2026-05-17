from pathlib import Path
from dotenv import load_dotenv
import os


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://dadosabertos.camara.leg.br/api/v2"
)

DEFAULT_YEAR = int(os.getenv("DEFAULT_YEAR", 2026))
DEFAULT_MONTH = int(os.getenv("DEFAULT_MONTH", 3))

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "camara_analytics")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

#Este arquivo centraliza as configurações do nosso projeto através do .env

