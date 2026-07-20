import random

from locators import BaseLocators, CategoryLocators
from pages import BasePage, HomePage, ProductPage
from playwright.sync_api import Page

from pages.cart.cart_data import Cartdata
from pages.commons.common_action import Commonaction
from pages.commons.common_data import Commondata
from pages.products.product_data import Productdata


class Productaction(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.common_data = Commondata(base_url)
        self.product_data = Productdata(base_url)
        self.cart_data = Cartdata(self.page, base_url)
        self.home_page = HomePage(self.page, base_url)
        self.product_page = ProductPage(self.page, base_url)
        self.common_action = Commonaction(self.page, base_url)

        self.bl = BaseLocators()
        self.cl = CategoryLocators()

        self.product_info = self.common_data.get_available_product()

    def random_product_selected(self):
        """홈(특가/전체) / 카테고리 경로를 랜덤으로 섞어 여러 상품을 장바구니에 담고 검증."""

        target_cnt = random.randint(1, 10)  # 1~5개 담기
        add_result = []

        for _ in range(target_cnt):
            # 매 반복마다 새 랜덤 상품으로 갱신 (생성자에서 한 번만 뽑힌 고정 캐시 재사용 방지)
            self.common_action.product_info = self.common_data.get_available_product()
            self.home_page.deal_product = self.home_page.home_data.get_deal_product()

            route = random.choice([ "category", "home_deal", "home_all"])  # ← 채움

            if route == "home_deal":
                product = self.home_page.deal_product_selected()  # 홈 특가 → 상세

            elif route == "home_all":
                product = self.common_action.all_product_selected()  # 홈 전체 → 상세

            else:
                self.common_action.category_selected()  # 카테고리 진입
                product = self.common_action.all_product_selected()  # → 상세

            # --- 여기는 모두 '상품 상세 페이지' ---
            product_code = product.get("target_product_code", 0)
            product_stock = product.get("target_product_stock", 0)

            before_qty = self.cart_data.get_qty_from_api(product_code)  # 담기 전 수량

            remaining = product_stock - before_qty

            if remaining <= 0:
                self.common_action.logo_selected()
                continue

            target_qty = self.product_data.get_random_qty(remaining) # 담을 수량

            self.product_page.increase_qty(target_qty - 1)  # 수량 조절 (기본 1개라 -1)
            self.product_page.add_to_cart()  # 담기
            self.product_page.add_success_toast()  # 토스트 확인

            expected_qty = before_qty + target_qty  # 누적 수량 값

            # --- 장바구니 API 로 검증 ---
            cart_response = self.cart_data.get_cart_response()
            cart_items = self.cart_data.get_cart_items()

            target = next(
                (ci for ci in cart_items if ci.get("cart_in_product_code") == product_code),
                None,
            )

            is_pass = (
                    cart_response.status == 200
                    and target is not None
                    and target.get("cart_in_product_qty") == expected_qty
            )

            add_result.append("Pass" if is_pass else "Fail")

            self.common_action.logo_selected()  # 홈 복귀 (다음 반복 준비)

        if not add_result:
            return True

        success = sum(1 for r in add_result if r == "Pass")
        return success == len(add_result)  # 실제 시도한 것들이 전부 통과하면 True

    def product_detail_add_to_cart(self, product_code, product_stock):
        """재고 있는 상품 상세로 이동해 담기 버튼 클릭 후 담은 상품 id 반환."""

        target_qty = self.product_data.get_random_qty(product_stock)
        print(f"상품 코드: {product_code}")
        print(f"상품 수량: {target_qty}")

        self.product_page.increase_qty(target_qty - 1)  # 스테퍼는 1에서 시작 → 최종 수량 = target_qty
        self.product_page.add_to_cart()
        self.product_page.add_success_toast()

        return product_code, target_qty



