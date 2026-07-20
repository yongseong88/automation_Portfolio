"""장바구니 API 서비스 래퍼.

UI 테스트에서 상태를 빠르게 준비(arrange)하거나, 순수 API 테스트에서 사용한다.
Playwright APIRequestContext 를 감싸 엔드포인트/페이로드를 한 곳에 모은다.
"""

from __future__ import annotations

from playwright.sync_api import APIRequestContext, APIResponse
from urllib.parse import quote




class AuthApi:
    def __init__(self, request: APIRequestContext):
        self.request = request

    def login(self, username: str, password: str) -> APIResponse:
        return self.request.post(
            "/api/login", data={"username": username, "password": password}
        )

    def me(self) -> APIResponse:
        return self.request.get("/api/me")

    def logout(self) -> APIResponse:
        return self.request.post("/api/logout")




class ProductApi:
    def __init__(self, request: APIRequestContext):
        self.request = request

    def list_categories(self) -> APIResponse:
        """카테고리 목록 조회 API 호출 (GET /api/categories)."""
        return self.request.get("/api/categories")


    def product_detail(self, product_id: int) -> APIResponse:
        """상품 상세 조회 API 호출 (GET /api/products/{product_id})."""
        return self.request.get(f"/api/products/{product_id}")

    def search_query(self, text: str) -> APIResponse:

        param_info = {
            "page_size": 50,
            "q": quote(text)
        }

        return self.request.get(f"/api/products/", params=param_info)


    def products_by_category(
        self,
        category: str,
        sort: str = "id",
        order: str = "asc",
        page_size: int = 50,
    ) -> APIResponse:
        """카테고리 필터 + 정렬 조건으로 상품 목록 조회 (GET /api/products)."""
        param_info = {
            "category": category,
            "sort": sort,
            "order": order,
            "page_size": page_size,
        }

        return self.request.get("/api/products", params=param_info)

    def sort_default(self, category: str, page_size: int = 50) -> APIResponse:
        """기본순(id 오름차순) 상품 목록 조회 (GET /api/products)."""
        return self.products_by_category(
            category=category, sort="id", order="asc", page_size=page_size
        )

    def sort_price_low(self, category: str, page_size: int = 50) -> APIResponse:
        """낮은 가격순(가격 오름차순) 상품 목록 조회 (GET /api/products)."""
        return self.products_by_category(
            category=category, sort="price", order="asc", page_size=page_size
        )

    def sort_price_high(self, category: str, page_size: int = 50) -> APIResponse:
        """높은 가격순(가격 내림차순) 상품 목록 조회 (GET /api/products)."""
        return self.products_by_category(
            category=category, sort="price", order="desc", page_size=page_size
        )

    def sort_name(self, category: str, page_size: int = 50) -> APIResponse:
        """이름순(이름 오름차순) 상품 목록 조회 (GET /api/products)."""
        return self.products_by_category(
            category=category, sort="name", order="asc", page_size=page_size
        )

class CartApi:
    def __init__(self, request: APIRequestContext):
        self.request = request

    def cart_add(self, product_id: int, qty: int = 1) -> APIResponse:
        """장바구니 담기 API 호출 (POST /api/cart, JSON 바디)."""
        return self.request.post(
            "/api/cart", data={"product_id": product_id, "qty": qty}
        )
    def cart_info(self) -> APIResponse:
        """장바구니 조회 API 호출 (GET /api/cart)."""
        return self.request.get("/api/cart")

    def cart_update(self, product_id: int, qty: int) -> APIResponse:
        """장바구니 수량 변경 API 호출 (PATCH /api/cart/{id}, 수량을 qty 로 설정)."""
        return self.request.patch(
            f"/api/cart/{product_id}", data={"qty": qty}
        )

    def cart_remove(self, product_id: int) -> APIResponse:
        """장바구니 상품 삭제 API 호출 (DELETE /api/cart/{id})."""
        return self.request.delete(f"/api/cart/{product_id}")

    def summary(self) -> dict:
        return self.request.get("/api/cart").json()


class OrderApi:
    def __init__(self, request: APIRequestContext):
        self.request = request

    def checkout_info(self) -> APIResponse:
        """체크아웃 정보 조회 API 호출 (GET /api/checkout)."""
        return self.request.get("/api/checkout")

    def get_order(self, order_id: int) -> APIResponse:
        """생성된 주문 조회 API 호출 (GET /api/orders/{order_id}, 성공 시 200)."""
        return self.request.get(f"/api/orders/{order_id}")


    def create_order(
        self,
        recipient_name: str = "테스터",
        phone: str = "010-0000-0000",
        address: str = "서울시 테스트구 테스트로 1",
        delivery_request: str = "",
        payment_method: str = "card",
    ) -> APIResponse:
        """주문 생성 API 호출 (POST /api/orders, 현재 장바구니로 주문)."""
        return self.request.post(
            "/api/orders",
            data={
                "recipient_name": recipient_name,
                "phone": phone,
                "address": address,
                "delivery_request": delivery_request,
                "payment_method": payment_method,
            },
        )
