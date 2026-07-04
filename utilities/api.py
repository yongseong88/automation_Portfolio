"""장바구니 API 서비스 래퍼.

UI 테스트에서 상태를 빠르게 준비(arrange)하거나, 순수 API 테스트에서 사용한다.
Playwright APIRequestContext 를 감싸 엔드포인트/페이로드를 한 곳에 모은다.
"""

from __future__ import annotations

from playwright.sync_api import APIRequestContext, APIResponse
from urllib.parse import quote



class ProductApi:
    def __init__(self, request: APIRequestContext):
        self.request = request

    def product_status(self, product_id: int) -> APIResponse:
        return self.request.get(f"/api/products/{product_id}")

    def search_query(self, text: str) -> APIResponse:

        param_info = {
            "page_size": 50,
            "q": quote(text)
        }

        return self.request.get(f"/api/products/", params=param_info)
