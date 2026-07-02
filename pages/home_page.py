"""홈 페이지 ('/')."""

from __future__ import annotations

from playwright.sync_api import Page, Locator

from locators import HomeLocators as L
from .base_page import BasePage


class HomePage(BasePage):
    PATH = "/"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.product_grid: Locator = page.get_by_test_id(L.PRODUCT_GRID)
        self.deal_grid: Locator = page.get_by_test_id(L.DEAL_GRID)
        self.search_title: Locator = page.get_by_test_id(L.SEARCH_TITLE)

    @property
    def cards(self) -> Locator:
        """전체 상품 그리드 안의 카드만 한정 (특가 그리드와 중복 카운트 방지)."""
        return self.product_grid.get_by_test_id(L.PRODUCT_CARD)

    @property
    def deal_cards(self) -> Locator:
        return self.deal_grid.get_by_test_id(L.PRODUCT_CARD)

    def open_first_product(self) -> None:
        self.cards.first.click()
