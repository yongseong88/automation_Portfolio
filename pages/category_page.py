"""카테고리 페이지 ('/category/{slug}')."""

from __future__ import annotations

from playwright.sync_api import Page, Locator

from locators import CategoryLocators as L
from .base_page import BasePage


class CategoryPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.title: Locator = page.get_by_test_id(L.TITLE)
        self.sort: Locator = page.get_by_test_id(L.SORT)
        self.cards: Locator = page.get_by_test_id(L.PRODUCT_CARD)
        self.prices: Locator = page.get_by_test_id(L.PRICE)

    def open(self, slug: str) -> "CategoryPage":
        super().open(f"/category/{slug}")
        return self

    def sort_by(self, value: str) -> "CategoryPage":
        """정렬 옵션 선택 후 재로딩 대기 (예: 'price:asc')."""
        self.sort.select_option(value)
        self.wait_loaded()
        return self

    def price_values(self) -> list[int]:
        """화면에 표시된 가격 텍스트('3,900원')를 정수 리스트로 변환."""
        return [
            int(t.replace(",", "").replace("원", ""))
            for t in self.prices.all_inner_texts()
        ]
