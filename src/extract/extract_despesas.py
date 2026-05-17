import json
from datetime import datetime, timezone

from src.extract.api_client import CamaraAPIClient
from src.extract.extract_deputados import extract_deputados
from src.utils.config import DEFAULT_MONTH, DEFAULT_YEAR
from src.utils.paths import BRONZE_DIR, ensure_directories


def extract_despesas_by_deputado(
    id_deputado: int,
    ano: int,
    mes: int,
) -> list[dict]:
    client = CamaraAPIClient()

    params = {
        "ano": ano,
        "mes": mes,
        "ordem": "ASC",
    }

    despesas = client.get_paginated(
        endpoint=f"/deputados/{id_deputado}/despesas",
        params=params,
        itens=100,
    )

    for despesa in despesas:
        despesa["idDeputado"] = id_deputado

    return despesas


def extract_despesas_periodo(
    ano: int = DEFAULT_YEAR,
    mes: int = DEFAULT_MONTH,
    limite_deputados: int | None = None,
) -> list[dict]:
    deputados = extract_deputados()

    if limite_deputados is not None:
        deputados = deputados[:limite_deputados]

    todas_despesas = []

    for index, deputado in enumerate(deputados, start=1):
        id_deputado = deputado["id"]
        nome_deputado = deputado.get("nome")

        print(
            f"[{index}/{len(deputados)}] "
            f"Extraindo despesas de {nome_deputado} ({id_deputado})"
        )

        despesas = extract_despesas_by_deputado(
            id_deputado=id_deputado,
            ano=ano,
            mes=mes,
        )

        todas_despesas.extend(despesas)

    return todas_despesas


def save_despesas_raw(
    despesas: list[dict],
    ano: int,
    mes: int,
) -> str:
    ensure_directories()

    data_carga = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    output_dir = (
        BRONZE_DIR
        / "despesas"
        / f"ano={ano}"
        / f"mes={mes:02d}"
        / f"dt_carga={data_carga}"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "despesas.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(despesas, file, ensure_ascii=False, indent=2)

    return str(output_path)


def main() -> None:
    ano = DEFAULT_YEAR
    mes = DEFAULT_MONTH

    despesas = extract_despesas_periodo(
        ano=ano,
        mes=mes,
        limite_deputados=10,
    )

    output_path = save_despesas_raw(
        despesas=despesas,
        ano=ano,
        mes=mes,
    )

    print(f"Despesas extraídas: {len(despesas)}")
    print(f"Arquivo salvo em: {output_path}")


if __name__ == "__main__":
    main()

#Responsavel pela extracao de despesas de um deputado especifico
