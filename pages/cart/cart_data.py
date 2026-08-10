import random
from utilities.File_read import Filereadutil
from utilities.api import CartApi


class Cartdata():
    def __init__(self, page, base_url: str):
        self.base_url = base_url
        # 브라우저 페이지의 APIRequestContext(page.request) 로 카트 API 호출 (쿠키/세션 공유)
        self.cart_api = CartApi(page.request)
        self.File_read_util = Filereadutil()

    def get_cart_response(self):
        """장바구니 API 응답 객체를 반환 (없으면 None)."""
        cart_response = self.cart_api.cart_info()
        return cart_response if cart_response else None

    def get_cart_items(self):
        """장바구니에 담긴 상품 목록을 dict 리스트로 반환."""
        response = self.get_cart_response()  # ← 괄호! 호출
        if response is None:
            return []

        cart_json = response.json()
        cart_items = cart_json.get("items", [])

        products = []
        for item in cart_items:
            products.append({
                "cart_in_product_code": item.get("id", 0),
                "cart_in_product_price": item.get("price", 0),
                "cart_in_product_qty": item.get("qty", ""),
                "cart_in_product_stock": item.get("stock", ""),
                # 단가(price)가 아니라 수량이 반영된 소계 → 합계 계산은 이 값으로 해야 한다
                "cart_in_product_line_total": item.get("line_total", 0),
            })

        return products

    def get_qty_from_api(self, product_code) -> int:
        """장바구니 API 에서 해당 상품의 현재 수량을 조회."""
        for item in self.get_cart_items():
            if item.get('cart_in_product_code') == product_code:
                return item.get('cart_in_product_qty', 0)

        return 0  # 장바구니에 없으면 0

    def get_shipping(self):
        """장바구니 총 결제금액을 반환."""
        response = self.get_cart_response()
        if response is None:
            return 0
        return response.json().get("shipping", 0)


    def get_cart_total(self):
        """장바구니 총 결제금액을 반환."""
        response = self.get_cart_response()
        if response is None:
            return 0
        return response.json().get("total", 0)

    def get_subtotal(self):
        """배송비를 뺀 상품 합계금액을 반환 (무료배송 판단 기준)."""
        response = self.get_cart_response()
        if response is None:
            return 0
        return response.json().get("subtotal", 0)

    def get_free_shipping_threshold(self):
        """무료배송 기준 금액을 API 에서 조회 (하드코딩 대신 서버 값 사용)."""
        response = self.get_cart_response()
        if response is None:
            return 0
        return response.json().get("free_shipping_threshold", 0)

    def clear_cart(self):
        """장바구니를 비운다.

        카트는 전역이라 앞선 테스트의 잔여물이 그대로 누적된다.
        금액 조건을 세우는 시나리오는 빈 카트에서 시작해야 결과가 결정적이다.
        """
        for item in self.get_cart_items():
            self.cart_api.cart_remove(item.get("cart_in_product_code"))

        return self.get_subtotal()