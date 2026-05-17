from pathlib import Path

#Aqui define os caminhos que serao padrao no projeto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"

BRONZE_DIR = RAW_DIR / "bronze"
SILVER_DIR = PROCESSED_DIR / "silver"


def ensure_directories() -> None:
    directories = [
        RAW_DIR,
        PROCESSED_DIR,
        OUTPUT_DIR,
        BRONZE_DIR,
        SILVER_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
