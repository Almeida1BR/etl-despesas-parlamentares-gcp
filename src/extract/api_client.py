import time
from typing import Any

import requests

from src.utils.config import API_BASE_URL

#Este código cria um cliente reutilizavel para a nossa API

class CamaraAPIClient:
    def __init__(self, base_url: str = API_BASE_URL, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        response = requests.get(url, params=params, timeout=self.timeout)

        response.raise_for_status()

        return response.json()

    def get_paginated(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        itens: int = 100,
        max_pages: int | None = None,
        sleep_seconds: float = 0.2,
    ) -> list[dict[str, Any]]:
        all_data = []
        page = 1

        while True:
            request_params = dict(params or {})
            request_params["itens"] = itens
            request_params["pagina"] = page

            response_json = self.get(endpoint, params=request_params)
            page_data = response_json.get("dados", [])

            if not page_data:
                break

            all_data.extend(page_data)

            if max_pages is not None and page >= max_pages:
                break

            page += 1
            time.sleep(sleep_seconds)

        return all_data
