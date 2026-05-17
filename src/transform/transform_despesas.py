import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.utils.config import DEFAULT_MONTH, DEFAULT_YEAR
from src.utils.logger import get_logger
from src.utils.paths import BRONZE_DIR, SILVER_DIR, ensure_directories


logger = get_logger(__name__)


def get_latest_despesas_file(ano: int, mes: int) -> Path:
    despesas_dir = BRONZE_DIR / "despesas" / f"ano={ano}" / f"mes={mes:02d}"

    files = sorted(
        despesas_dir.glob("dt_carga=*/despesas.json"),
        reverse=True,
    )

    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo de despesas encontrado em {despesas_dir}"
        )

    return files[0]


def load_despesas_raw(input_path: Path) -> list[dict]:
    logger.info("Lendo arquivo Bronze de despesas: %s", input_path)

    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    logger.info("Registros brutos de despesas carregados: %s", len(data))

    return data


def transform_despesas(data: list[dict], ano: int, mes: int) -> pd.DataFrame:
    logger.info("Iniciando transformação de despesas")

    df = pd.DataFrame(data)

    if df.empty:
        logger.warning("DataFrame de despesas está vazio")
        return df

    rename_columns = {
        "idDeputado": "id_deputado",
        "ano": "ano",
        "mes": "mes",
        "tipoDespesa": "tipo_despesa",
        "codDocumento": "cod_documento",
        "tipoDocumento": "tipo_documento",
        "codTipoDocumento": "cod_tipo_documento",
        "dataDocumento": "data_documento",
        "numDocumento": "num_documento",
        "valorDocumento": "valor_documento",
        "urlDocumento": "url_documento",
        "nomeFornecedor": "nome_fornecedor",
        "cnpjCpfFornecedor": "cnpj_cpf_fornecedor",
        "valorLiquido": "valor_liquido",
        "valorGlosa": "valor_glosa",
        "numRessarcimento": "num_ressarcimento",
        "codLote": "cod_lote",
        "parcela": "parcela",
    }

    df = df.rename(columns=rename_columns)

    expected_columns = [
        "id_deputado",
        "ano",
        "mes",
        "tipo_despesa",
        "cod_documento",
        "tipo_documento",
        "cod_tipo_documento",
        "data_documento",
        "num_documento",
        "valor_documento",
        "url_documento",
        "nome_fornecedor",
        "cnpj_cpf_fornecedor",
        "valor_liquido",
        "valor_glosa",
        "num_ressarcimento",
        "cod_lote",
        "parcela",
    ]

    for column in expected_columns:
        if column not in df.columns:
            df[column] = None

    df = df[expected_columns]

    integer_columns = [
        "id_deputado",
        "ano",
        "mes",
        "cod_documento",
        "cod_tipo_documento",
        "cod_lote",
        "parcela",
    ]

    for column in integer_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

    numeric_columns = [
        "valor_documento",
        "valor_liquido",
        "valor_glosa",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["data_documento"] = pd.to_datetime(
        df["data_documento"],
        errors="coerce",
    ).dt.date

    df["ano_referencia"] = ano
    df["mes_referencia"] = mes
    df["data_carga"] = datetime.now(timezone.utc)

    df = df.drop_duplicates(
        subset=[
            "id_deputado",
            "ano",
            "mes",
            "cod_documento",
            "cod_lote",
            "parcela",
        ],
        keep="last",
    )

    logger.info("Transformação de despesas finalizada. Registros tratados: %s", len(df))

    return df


def save_despesas_silver(df: pd.DataFrame, ano: int, mes: int) -> str:
    ensure_directories()

    output_dir = SILVER_DIR / "despesas" / f"ano={ano}" / f"mes={mes:02d}"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "despesas.parquet"

    df.to_parquet(output_path, index=False)

    logger.info("Arquivo Silver de despesas salvo em: %s", output_path)

    return str(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transforma despesas parlamentares da camada Bronze para Silver."
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

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = get_latest_despesas_file(
        ano=args.ano,
        mes=args.mes,
    )

    raw_data = load_despesas_raw(input_path)

    df_despesas = transform_despesas(
        data=raw_data,
        ano=args.ano,
        mes=args.mes,
    )

    output_path = save_despesas_silver(
        df=df_despesas,
        ano=args.ano,
        mes=args.mes,
    )

    logger.info("Processo concluído")
    logger.info("Arquivo de entrada: %s", input_path)
    logger.info("Arquivo de saída: %s", output_path)
    logger.info("Total de despesas tratadas: %s", len(df_despesas))


if __name__ == "__main__":
    main()
