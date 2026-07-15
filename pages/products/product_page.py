"""상품 상세 페이지 ('/product/{product_id}')."""

from __future__ import annotations
from playwright.sync_api import Page, Locator
from locators import ProductLocators as pl, ProductLocators
from pages.base_page import BasePage
from pages.commons.common_action import Commonaction
from pages.commons.common_data import Commondata
from pages.products.product_data import Productdata


class ProductPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        # self.detail: Locator = page.get_by_test_id(pl.DETAIL)
        # self.name: Locator = page.get_by_test_id(pl.NAME)
        # self.price: Locator = page.get_by_test_id(pl.PRICE)
        # self.not_found: Locator = page.get_by_test_id(pl.NOT_FOUND)
        self.common_data = Commondata(base_url)
        self.product_data = Productdata(base_url)
        self.common_action = Commonaction(self.page, base_url)
        self.pl = ProductLocators()

        self.product_info = self.common_data.get_available_product()

    def increase_qty(self, times: int) -> None:
        """수량 스테퍼(+) 를 times 만큼 클릭한다."""
        for _ in range(times):
            self.get_element_by_locator(self.pl.qty_plus).click()

    def decrease_qty(self, times: int) -> None:
        """수량 스테퍼(-) 를 times 만큼 클릭한다."""
        for _ in range(times):
            self.get_element_by_locator(self.pl.qty_minus).click()

    def add_to_cart(self) -> None:
        """담기 버튼을 클릭한다."""
        self.get_element_by_locator(self.pl.add_cart).click()

    def add_success_toast(self) -> None:
        """담기 버튼을 클릭한다."""
        add_toast = self.get_element_by_locator(self.pl.add_cart_toast)
        self.is_displayed(add_toast)  # 담기 완료(토스트) 대기

