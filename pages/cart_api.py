"""장바구니 API 서비스 래퍼.

UI 테스트에서 상태를 빠르게 준비(arrange)하거나, 순수 API 테스트에서 사용한다.
Playwright APIRequestContext 를 감싸 엔드포인트/페이로드를 한 곳에 모은다.
"""

from __future__ import annotations

from playwright.sync_api import APIRequestContext, APIResponse


class CartApi:
    def __init__(self, request: APIRequestContext):
        self.request = request

    def add(self, product_id: int, qty: int = 1) -> APIResponse:
        return self.request.post(
            "/api/cart", data={"product_id": product_id, "qty": qty}
        )

    def summary(self) -> dict:
        return self.request.get("/api/cart").json()

    def remove(self, product_id: int) -> APIResponse:
        return self.request.delete(f"/api/cart/{product_id}")
