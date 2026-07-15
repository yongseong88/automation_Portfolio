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
            })

        return products

    def get_qty_from_api(self, product_code) -> int:
        """장바구니 API 에서 해당 상품의 현재 수량을 조회."""
        for item in self.get_cart_items():
            if item.get('cart_in_product_code') == product_code:
                return item.get('cart_in_product_qty', 0)
        return 0  # 장바구니에 없으면 0

    def get_cart_total(self):
        """장바구니 총 결제금액을 반환."""
        response = self.get_cart_response()  # ← 괄호! 호출
        if response is None:
            return 0
        return response.json().get("total", 0)

    # def remove_random_items(self):
    #     """장바구니에서 랜덤한 개수의 상품을 골라 제거 (뼈대)."""
    #     cart_items = self.get_cart_items()
    #
    #     if not cart_items:  # 빈 장바구니 방어
    #         return
    #
    #     random.shuffle(cart_items)  # 먼저 섞고
    #     random_cnt = random.randint(1, len(cart_items))  # 1~전체 개
    #     target_items = cart_items[:random_cnt]  # 앞에서 n개
    #
    #     return target_items