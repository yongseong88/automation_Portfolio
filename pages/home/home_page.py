"""홈 페이지 ('/')."""

from __future__ import annotations
from playwright.sync_api import Page, Locator
from locators import BaseLocators, HomeLocators
from pages.base_page import BasePage
from pages.commons.common_action import Commonaction
from pages.commons.common_data import Commondata
from pages.home.home_data import Homedata


class HomePage(BasePage):
    PATH = "/"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        # self.product_grid: Locator = page.get_by_test_id(hl.PRODUCT_GRID)
        # self.deal_grid: Locator = page.get_by_test_id(hl.DEAL_GRID)
        # self.search_title: Locator = page.get_by_test_id(hl.SEARCH_TITLE)
        self.home_data = Homedata(base_url)
        self.common_data = Commondata(base_url)
        self.common_action = Commonaction(self.page, base_url)
        self.hl = HomeLocators()
        self.bl = BaseLocators()

        self.deal_product = self.home_data.get_deal_product()
        self.product_info = self.common_data.get_available_product()

    def deal_product_selected(self):
        """ 특가 상품 클릭 """
        deal_product_code = self.deal_product['product_id']
        deal_product_stock = self.deal_product['product_stock']
        print(f"특가 상품 코드: {deal_product_code}")
        print(f"특가 상품 수량: {deal_product_code}")

        self.wait_loaded(self.bl.loading)
        self.get_element_by_locator(self.hl.deal_grid(deal_product_code)).click()

        return {
            "target_product_code" : deal_product_code,
            "target_product_stock" : deal_product_stock
        }

    def all_product_selected(self):
        """ 전체 상품 클릭 """

        target_prd = self.common_action.all_product_selected()
        return target_prd








    #
    #
    #
    #
    #
    #
    # @property
    # def cards(self) -> Locator:
    #     """전체 상품 그리드 안의 카드만 한정 (특가 그리드와 중복 카운트 방지)."""
    #     return self.product_grid.get_by_test_id(hl.PRODUCT_CARD)
    #
    # @property
    # def deal_cards(self) -> Locator:
    #     return self.deal_grid.get_by_test_id(hl.PRODUCT_CARD)
    #
    # def open_first_product(self) -> None:
    #     self.cards.first.click()
