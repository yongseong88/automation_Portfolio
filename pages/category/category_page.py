"""카테고리 페이지 ('/category/{slug}')."""

from __future__ import annotations

from playwright.sync_api import Page, Locator

from locators import CategoryLocators, BaseLocators
from pages.base_page import BasePage
from pages.commons.common_action import Commonaction
from pages.commons.common_data import Commondata


class CategoryPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.common_data = Commondata(base_url)
        self.common_action = Commonaction(self.page, base_url)
        self.cl = CategoryLocators()
        self.bl = BaseLocators()

        self.product_info = self.common_data.get_available_product()
        # self.title: Locator = page.get_by_test_id(L.TITLE)
        # self.sort: Locator = page.get_by_test_id(L.SORT)
        # self.cards: Locator = page.get_by_test_id(L.PRODUCT_CARD)
        # self.prices: Locator = page.get_by_test_id(L.PRICE)

    def default_sort(self):
        """기본순(id 오름차순) 정렬 선택 후 재로딩 대기 (예: 'id:asc')."""
        target_prd_category = self.common_action.category_selected()

        self.get_element_by_locator(self.cl.sort_dropdown).select_option(self.cl.default_sort)
        self.wait_loaded(self.bl.loading)

        return target_prd_category

    def price_asc_sort(self):
        """정렬 옵션 선택 후 재로딩 대기 (예: 'price:asc')."""
        target_prd_category = self.common_action.category_selected()

        self.get_element_by_locator(self.cl.sort_dropdown).select_option(self.cl.price_asc)
        self.wait_loaded(self.bl.loading)

        return target_prd_category

    def price_desc_sort(self):
        """정렬 옵션 선택 후 재로딩 대기 (예: 'price:desc')."""
        target_prd_category = self.common_action.category_selected()

        self.get_element_by_locator(self.cl.sort_dropdown).select_option(self.cl.price_desc)
        self.wait_loaded(self.bl.loading)

        return target_prd_category

    def name_asc_sort(self):
        """정렬 옵션 선택 후 재로딩 대기 (예: 'name:asc')."""
        target_prd_category = self.common_action.category_selected()

        self.get_element_by_locator(self.cl.sort_dropdown).select_option(self.cl.name_asc)
        self.wait_loaded(self.bl.loading)

        return target_prd_category

    def category_product_selected(self):
        """ 전체 상품 클릭 """
        self.common_action.category_selected()
        target_prd = self.common_action.all_product_selected()

        return target_prd



    # def category_selected(self):
    #     all_product = self.common_data.get_available_product()
    #     target_prd_category = all_product['product_category']
    #     category_keyword = self.cl.category(target_prd_category)
    #
    #     self.common_action.wait_products_loaded()
    #     self.get_element_by_locator(category_keyword).click()
    #     self.wait_loaded(self.bl.loading)
    #
    #     # API 검증에서 재사용할 수 있도록 선택된 카테고리 slug 반환
    #     return target_prd_category
    #

    # def open(self, slug: str) -> "CategoryPage":
    #     super().open(f"/category/{slug}")
    #     return self



    def price_values(self) -> list[int]:
        """화면에 표시된 가격 텍스트('3,900원')를 정수 리스트로 변환."""
        return [
            int(t.replace(",", "").replace("원", ""))
            for t in self.prices.all_inner_texts()
        ]
