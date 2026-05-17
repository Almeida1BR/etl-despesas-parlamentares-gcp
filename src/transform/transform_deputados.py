import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.utils.logger import get_logger
from src.utils.paths import BRONZE_DIR, SILVER_DIR, ensure_directories


logger = get_logger(__name__)


def get_latest_deputados_file() -> Path:
    deputados_dir = BRONZE_DIR / "deputados"

    files = sorted(
        deputados_dir.glob("dt_carga=*/deputados.json"),
        reverse=True,
    )

    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo de deputados encontrado em {deputados_dir}"
        )

    return files[0]


def load_deputados_raw(input_path: Path) -> list[dict]:
    logger.info("Lendo arquivo Bronze de deputados: %s", input_path)

    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    logger.info("Registros brutos de deputados carregados: %s", len(data))

    return data


def transform_deputados(data: list[dict]) -> pd.DataFrame:
    logger.info("Iniciando transformação de deputados")

    df = pd.DataFrame(data)

    rename_columns = {
        "id": "id_deputado",
        "uri": "uri_deputado",
        "nome": "nome_deputado",
        "siglaPartido": "sigla_partido",
        "uriPartido": "uri_partido",
        "siglaUf": "sigla_uf",
        "idLegislatura": "id_legislatura",
        "urlFoto": "url_foto",
        "email": "email",
    }

    df = df.rename(columns=rename_columns)

    expected_columns = [
        "id_deputado",
        "uri_deputado",
        "nome_deputado",
        "sigla_partido",
        "uri_partido",
        "sigla_uf",
        "id_legislatura",
        "url_foto",
        "email",
    ]

    for column in expected_columns:
        if column not in df.columns:
            df[column] = None

    df = df[expected_columns]

    df["id_deputado"] = pd.to_numeric(df["id_deputado"], errors="coerce").astype("Int64")
    df["id_legislatura"] = pd.to_numeric(df["id_legislatura"], errors="coerce").astype("Int64")

    df["data_carga"] = datetime.now(timezone.utc)

    df = df.drop_duplicates(subset=["id_deputado"])

    logger.info("Transformação de deputados finalizada. Registros tratados: %s", len(df))

    return df


def save_deputados_silver(df: pd.DataFrame) -> str:
    ensure_directories()

    output_dir = SILVER_DIR / "deputados"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "deputados.parquet"

    df.to_parquet(output_path, index=False)

    logger.info("Arquivo Silver de deputados salvo em: %s", output_path)

    return str(output_path)


def main() -> None:
    input_path = get_latest_deputados_file()
    raw_data = load_deputados_raw(input_path)
    df_deputados = transform_deputados(raw_data)
    output_path = save_deputados_silver(df_deputados)

    logger.info("Processo concluído")
    logger.info("Arquivo de entrada: %s", input_path)
    logger.info("Arquivo de saída: %s", output_path)
    logger.info("Total de deputados tratados: %s", len(df_deputados))


if __name__ == "__main__":
    main()
