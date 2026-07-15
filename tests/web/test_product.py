"""상품 상세 페이지 UI 테스트 (POM 사용)."""

import re

import pytest
from playwright.sync_api import Page, expect
from pages import HomePage, ProductPage, CategoryPage
from pages.products.product_actions import Productaction
from utilities.api import ProductApi, CartApi

SOLD_OUT_PRODUCT_ID = 13  # 크루아상 = 품절(stock 0)
IN_STOCK_PRODUCT_ID = 1  # 유기농 시금치


@pytest.mark.ui_journey
class TestProduct():# BaseTest 상속 없이도 됨]
    def test_home_deal_product_cart_add(self):
        """카테고리 선택 후 해당 카테고리 상품 목록 API 응답을 검증한다."""
        home = HomePage(self.page, self.base_url)
        product_action = Productaction(self.page, self.base_url)
        res = CartApi(self.api)

        deal_product = home.deal_product_selected()
        deal_product_code = deal_product['target_product_code']
        deal_product_qty = deal_product['target_product_stock']

        deal_code, added_qty = product_action.product_detail_add_to_cart(deal_product_code, deal_product_qty)
        cart_response = res.cart_info()

        body = cart_response.json()
        target = next((item for item in body["items"] if item["id"] == deal_code), None)

        print(f"장바구니 조회 api 응답: {cart_response.status}")

        # assert cart_add_response.status == 200, "카테고리 상품 목록 api 호출 실패"
        assert cart_response.status == 200, "장바구니 조회 api 호출 실패"
        assert target is not None, "담은 상품이 장바구니에 없음"
        assert target["qty"] == added_qty, "담은 수량이 조회 결과와 일치하지 않음"

    def test_home_all_product_cart_add(self):
        """카테고리 선택 후 해당 카테고리 상품 목록 API 응답을 검증한다."""
        home = HomePage(self.page, self.base_url)
        product_action = Productaction(self.page, self.base_url)
        res = CartApi(self.api)

        home_all_product = home.all_product_selected()
        home_all_product_code = home_all_product['target_product_code']
        home_all_product_qty = home_all_product['target_product_stock']

        deal_code, added_qty = product_action.product_detail_add_to_cart(home_all_product_code, home_all_product_qty)
        # cart_add_response = res.cart_add(deal_product_code, deal_product_qty)
        cart_response = res.cart_info()

        body = cart_response.json()
        target = next((item for item in body["items"] if item["id"] == deal_code), None)

        print(f"장바구니 조회 api 응답: {cart_response.status}")

        assert cart_response.status == 200, "장바구니 조회 api 호출 실패"
        assert target is not None, "담은 상품이 장바구니에 없음"
        assert target["qty"] == added_qty, "담은 수량이 조회 결과와 일치하지 않음"

    def test_category_product_cart_add(self):
        """카테고리에서 상품 선택 후 상세에서 담고 장바구니 조회로 담은 수량을 검증한다."""
        category = CategoryPage(self.page, self.base_url)
        product_action = Productaction(self.page, self.base_url)
        res = CartApi(self.api)

        category_product = category.category_product_selected()
        category_product_code = category_product['target_product_code']
        category_product_qty = category_product['target_product_stock']

        category_code, added_qty = product_action.product_detail_add_to_cart(category_product_code, category_product_qty)
        cart_response = res.cart_info()

        body = cart_response.json()
        target = next((item for item in body["items"] if item["id"] == category_code), None)

        print(f"장바구니 조회 api 응답: {cart_response.status}")

        assert cart_response.status == 200, "장바구니 조회 api 호출 실패"
        assert target is not None, "담은 상품이 장바구니에 없음"
        assert target["qty"] == added_qty, "담은 수량이 조회 결과와 일치하지 않음"

    def test_random_product_cart_add(self):
        product_action = Productaction(self.page, self.base_url)
        res = CartApi(self.api)

        product_add_result = product_action.random_product_selected()
        assert product_add_result == True, "장바구니 담기 실패"









# def test_navigate_home_to_detail(page: Page, base_url: str):
#     home = HomePage(page, base_url).open()
#     home.wait_loaded()
#     home.open_first_product()
#     expect(page).to_have_url(re.compile(r"/product/\d+"))
#     # 같은 page 위에서 상세 페이지 객체로 검증
#     product = ProductPage(page, base_url)
#     expect(product.name).to_be_visible()
#
#
# def test_detail_404_for_unknown_product(page: Page, base_url: str):
#     product = ProductPage(page, base_url).open(99999)
#     expect(product.not_found).to_be_visible()
#     expect(product.detail).to_be_hidden()
#
#
# def test_sold_out_button_is_disabled(page: Page, base_url: str):
#     product = ProductPage(page, base_url).open(SOLD_OUT_PRODUCT_ID)
#     expect(product.sold_out_btn).to_be_disabled()
#
#
# def test_quantity_stepper_min_is_one(page: Page, base_url: str):
#     product = ProductPage(page, base_url).open(IN_STOCK_PRODUCT_ID)
#     expect(product.qty_minus).to_be_disabled()  # 1에서 더 못 내림
#     product.increase_qty()
#     expect(product.qty).to_have_text("2")
#     expect(product.qty_minus).to_be_enabled()
#
#
# def test_add_to_cart_updates_badge(page: Page, base_url: str):
#     product = ProductPage(page, base_url).open(IN_STOCK_PRODUCT_ID)
#     product.increase_qty()  # qty=2
#     product.add_to_cart()
#     expect(product.toast_ok).to_be_visible()
#     expect(product.cart_count).to_have_text("2")
