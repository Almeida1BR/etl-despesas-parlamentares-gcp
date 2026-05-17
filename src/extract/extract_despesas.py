import argparse
import json
from datetime import datetime, timezone

from src.extract.api_client import CamaraAPIClient
from src.extract.extract_deputados import extract_deputados
from src.utils.config import DEFAULT_MONTH, DEFAULT_YEAR
from src.utils.logger import get_logger
from src.utils.paths import BRONZE_DIR, ensure_directories


logger = get_logger(__name__)


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
    deputados: list[dict] | None = None,
) -> list[dict]:
    if deputados is None:
        deputados = extract_deputados()

    if limite_deputados is not None:
        deputados = deputados[:limite_deputados]

    todas_despesas = []
    total_deputados = len(deputados)
    total_com_erro = 0

    logger.info(
        "Iniciando extração de despesas. Ano=%s, mês=%s, deputados=%s",
        ano,
        mes,
        total_deputados,
    )

    for index, deputado in enumerate(deputados, start=1):
        id_deputado = deputado["id"]
        nome_deputado = deputado.get("nome")

        logger.info(
            "[%s/%s] Extraindo despesas de %s (%s)",
            index,
            total_deputados,
            nome_deputado,
            id_deputado,
        )

        try:
            despesas = extract_despesas_by_deputado(
                id_deputado=id_deputado,
                ano=ano,
                mes=mes,
            )

            todas_despesas.extend(despesas)

            logger.info(
                "Deputado %s (%s): %s despesas extraídas",
                nome_deputado,
                id_deputado,
                len(despesas),
            )

        except Exception as exc:
            total_com_erro += 1

            logger.exception(
                "Erro ao extrair despesas de %s (%s): %s",
                nome_deputado,
                id_deputado,
                exc,
            )

    logger.info("Extração de despesas finalizada")
    logger.info("Total de despesas extraídas: %s", len(todas_despesas))
    logger.info("Deputados com erro: %s", total_com_erro)

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

    logger.info("Arquivo de despesas salvo em: %s", output_path)

    return str(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrai despesas parlamentares da API Dados Abertos da Câmara."
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
        default=10,
        help="Quantidade máxima de deputados a processar. Use 0 para processar todos.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    limite_deputados = (
        None if args.limite_deputados == 0 else args.limite_deputados
    )

    despesas = extract_despesas_periodo(
        ano=args.ano,
        mes=args.mes,
        limite_deputados=limite_deputados,
    )

    output_path = save_despesas_raw(
        despesas=despesas,
        ano=args.ano,
        mes=args.mes,
    )

    logger.info("Processo concluído")
    logger.info("Ano/mês: %s/%s", args.ano, f"{args.mes:02d}")
    logger.info("Despesas extraídas: %s", len(despesas))
    logger.info("Arquivo salvo em: %s", output_path)


if __name__ == "__main__":
    main()