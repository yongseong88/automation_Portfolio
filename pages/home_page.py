"""홈 페이지 ('/')."""

from __future__ import annotations
from playwright.sync_api import Page, Locator
from locators import BaseLocators as bl
from locators import HomeLocators as hl
from .base_page import BasePage
from .commons.common_data import Commondata


class HomePage(BasePage):
    PATH = "/"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.product_grid: Locator = page.get_by_test_id(hl.PRODUCT_GRID)
        self.deal_grid: Locator = page.get_by_test_id(hl.DEAL_GRID)
        self.search_title: Locator = page.get_by_test_id(hl.SEARCH_TITLE)
        self.common_data = Commondata(base_url)

    def deal_product_selected(self):
        deal_product_id = self.common_data.get_deal_product()

        self.open()
        self.wait_loaded()

        deal_product_grid = self.get_element_by_id(hl.DEAL_GRID)
        deal_product_grid.locator(f'[data-id="{deal_product_id}"]').click()
        return deal_product_id

    def all_product_selected(self):
        all_product = self.common_data.get_all_product()
        target_prd_id = all_product['product_id']

        self.open()
        self.wait_loaded()

        all_product_grid = self.get_element_by_id(hl.PRODUCT_GRID)
        all_product_grid.locator(f'[data-id="{target_prd_id}"]').click()

        return target_prd_id

    def product_search(self):
        all_product = self.common_data.get_all_product()
        target_prd_name = all_product['product_name']

        self.open()
        self.wait_loaded()

        self.input_text(bl.SEARCH, target_prd_name)
        self.press_key(bl.SEARCH, "Enter")
        self.wait_loaded()

        return target_prd_name





    @property
    def cards(self) -> Locator:
        """전체 상품 그리드 안의 카드만 한정 (특가 그리드와 중복 카운트 방지)."""
        return self.product_grid.get_by_test_id(hl.PRODUCT_CARD)

    @property
    def deal_cards(self) -> Locator:
        return self.deal_grid.get_by_test_id(hl.PRODUCT_CARD)

    def open_first_product(self) -> None:
        self.cards.first.click()
