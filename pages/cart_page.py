"""장바구니 페이지 ('/cart')."""

from __future__ import annotations

from playwright.sync_api import Page, Locator

from locators import CartLocators as L
from .base_page import BasePage


class CartPage(BasePage):
    PATH = "/cart"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.empty: Locator = page.get_by_test_id(L.EMPTY)
        self.items: Locator = page.get_by_test_id(L.ITEM)
        self.subtotal: Locator = page.get_by_test_id(L.SUBTOTAL)
        self.shipping: Locator = page.get_by_test_id(L.SHIPPING)
        self.total: Locator = page.get_by_test_id(L.TOTAL)
        self.remove_btn: Locator = page.get_by_test_id(L.ITEM_REMOVE)
        self.item_qty: Locator = page.get_by_test_id(L.ITEM_QTY)
        self.item_plus: Locator = page.get_by_test_id(L.ITEM_PLUS)
        self.item_minus: Locator = page.get_by_test_id(L.ITEM_MINUS)

    def remove_first(self) -> None:
        self.remove_btn.first.click()
