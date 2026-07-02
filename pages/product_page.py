"""상품 상세 페이지 ('/product/{product_id}')."""

from __future__ import annotations

from playwright.sync_api import Page, Locator

from locators import ProductLocators as L
from .base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.detail: Locator = page.get_by_test_id(L.DETAIL)
        self.name: Locator = page.get_by_test_id(L.NAME)
        self.price: Locator = page.get_by_test_id(L.PRICE)
        self.not_found: Locator = page.get_by_test_id(L.NOT_FOUND)
        # 수량 스테퍼
        self.qty: Locator = page.get_by_test_id(L.QTY)
        self.qty_plus: Locator = page.get_by_test_id(L.QTY_PLUS)
        self.qty_minus: Locator = page.get_by_test_id(L.QTY_MINUS)
        # 담기 / 품절
        self.add_to_cart_btn: Locator = page.get_by_test_id(L.ADD_TO_CART)
        self.sold_out_btn: Locator = page.get_by_test_id(L.SOLD_OUT_BTN)
        self.toast_ok: Locator = page.get_by_test_id(L.TOAST_OK)

    def open(self, product_id: int) -> "ProductPage":
        super().open(f"/product/{product_id}")
        return self

    def increase_qty(self, times: int = 1) -> None:
        for _ in range(times):
            self.qty_plus.click()

    def decrease_qty(self, times: int = 1) -> None:
        for _ in range(times):
            self.qty_minus.click()

    def add_to_cart(self) -> None:
        self.add_to_cart_btn.click()
