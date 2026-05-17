import json
from datetime import datetime, timezone

from src.extract.api_client import CamaraAPIClient
from src.utils.paths import BRONZE_DIR, ensure_directories
#Aqui extrairemos os depois usando paginacao e salvaremos nosso RAW em JSON

def extract_deputados() -> list[dict]:
    client = CamaraAPIClient()

    params = {
        "ordem": "ASC",
        "ordenarPor": "nome",
    }

    deputados = client.get_paginated(
        endpoint="/deputados",
        params=params,
        itens=100,
    )

    return deputados


def save_deputados_raw(deputados: list[dict]) -> str:
    ensure_directories()

    data_carga = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    output_dir = BRONZE_DIR / "deputados" / f"dt_carga={data_carga}"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "deputados.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(deputados, file, ensure_ascii=False, indent=2)

    return str(output_path)


def main() -> None:
    deputados = extract_deputados()
    output_path = save_deputados_raw(deputados)

    print(f"Deputados extraídos: {len(deputados)}")
    print(f"Arquivo salvo em: {output_path}")


if __name__ == "__main__":
    main()