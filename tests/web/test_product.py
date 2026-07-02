"""상품 상세 페이지 UI 테스트 (POM 사용)."""

import re

from playwright.sync_api import Page, expect

from pages import HomePage, ProductPage

SOLD_OUT_PRODUCT_ID = 13  # 크루아상 = 품절(stock 0)
IN_STOCK_PRODUCT_ID = 1  # 유기농 시금치


def test_navigate_home_to_detail(page: Page, base_url: str):
    home = HomePage(page, base_url).open()
    home.wait_loaded()
    home.open_first_product()
    expect(page).to_have_url(re.compile(r"/product/\d+"))
    # 같은 page 위에서 상세 페이지 객체로 검증
    product = ProductPage(page, base_url)
    expect(product.name).to_be_visible()


def test_detail_404_for_unknown_product(page: Page, base_url: str):
    product = ProductPage(page, base_url).open(99999)
    expect(product.not_found).to_be_visible()
    expect(product.detail).to_be_hidden()


def test_sold_out_button_is_disabled(page: Page, base_url: str):
    product = ProductPage(page, base_url).open(SOLD_OUT_PRODUCT_ID)
    expect(product.sold_out_btn).to_be_disabled()


def test_quantity_stepper_min_is_one(page: Page, base_url: str):
    product = ProductPage(page, base_url).open(IN_STOCK_PRODUCT_ID)
    expect(product.qty_minus).to_be_disabled()  # 1에서 더 못 내림
    product.increase_qty()
    expect(product.qty).to_have_text("2")
    expect(product.qty_minus).to_be_enabled()


def test_add_to_cart_updates_badge(page: Page, base_url: str):
    product = ProductPage(page, base_url).open(IN_STOCK_PRODUCT_ID)
    product.increase_qty()  # qty=2
    product.add_to_cart()
    expect(product.toast_ok).to_be_visible()
    expect(product.cart_count).to_have_text("2")
