import time
from typing import Any

import requests

from src.utils.config import API_BASE_URL
from src.utils.logger import get_logger


logger = get_logger(__name__)


class CamaraAPIClient:
    def __init__(
        self,
        base_url: str = API_BASE_URL,
        timeout: int = 60,
        max_retries: int = 3,
        retry_sleep_seconds: float = 3.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_sleep_seconds = retry_sleep_seconds

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                )

                response.raise_for_status()

                return response.json()

            except requests.exceptions.RequestException as exc:
                last_exception = exc

                logger.warning(
                    "Falha na requisição. Tentativa %s/%s | URL=%s | Params=%s | Erro=%s",
                    attempt,
                    self.max_retries,
                    url,
                    params,
                    exc,
                )

                if attempt < self.max_retries:
                    time.sleep(self.retry_sleep_seconds)

        logger.error(
            "Requisição falhou após %s tentativas | URL=%s | Params=%s",
            self.max_retries,
            url,
            params,
        )

        raise last_exception

    def get_paginated(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        itens: int = 100,
        max_pages: int | None = None,
        sleep_seconds: float = 0.5,
    ) -> list[dict[str, Any]]:
        all_data = []
        page = 1

        while True:
            request_params = dict(params or {})
            request_params["itens"] = itens
            request_params["pagina"] = page

            logger.info(
                "Consultando endpoint paginado | endpoint=%s | pagina=%s",
                endpoint,
                page,
            )

            response_json = self.get(endpoint, params=request_params)
            page_data = response_json.get("dados", [])

            if not page_data:
                logger.info(
                    "Paginação finalizada | endpoint=%s | ultima_pagina=%s",
                    endpoint,
                    page,
                )
                break

            all_data.extend(page_data)

            logger.info(
                "Página processada | endpoint=%s | pagina=%s | registros=%s | total_acumulado=%s",
                endpoint,
                page,
                len(page_data),
                len(all_data),
            )

            if max_pages is not None and page >= max_pages:
                logger.info(
                    "Limite máximo de páginas atingido | endpoint=%s | max_pages=%s",
                    endpoint,
                    max_pages,
                )
                break

            page += 1
            time.sleep(sleep_seconds)

        return all_data
    #Este código cria um cliente reutilizavel para a nossa API
