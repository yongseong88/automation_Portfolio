import random

from locators import BaseLocators, CategoryLocators
from pages import BasePage
from playwright.sync_api import Page, Locator
from pages.commons.common_data import Commondata

class Commonaction(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.common_data = Commondata(base_url)
        self.bl = BaseLocators()
        self.cl = CategoryLocators()

        self.product_info = self.common_data.get_available_product()

    def wait_products_loaded(self):
        """상품 카드가 보일 때까지 대기 (홈/카테고리 공용)."""
        card = self.get_element_by_locator(self.bl.card_list)
        self.wait_visible(card.first)

    def logo_selected(self):
        self.get_element_by_locator(self.bl.logo).click()
        self.wait_loaded(self.bl.loading)
        assert self.check_url(f"{self.base_url}/"), "로고 클릭 후 홈으로 이동하지 않음"
        self.wait_products_loaded()


    def category_selected(self):
        """ 카테고리 클릭 (홈, 카테고리 사용 가능) """

        target_prd_category = self.product_info['product_category']
        category_keyword = self.cl.category(target_prd_category)

        self.wait_products_loaded()
        self.get_element_by_locator(category_keyword).click()
        self.wait_loaded(self.bl.loading)

        # API 검증에서 재사용할 수 있도록 선택된 카테고리 slug 반환
        return target_prd_category

    def product_search(self):
        """ 상품 검색 (홈, 카테고리 사용 가능) """
        # all_product = self.common_data.get_available_product()
        target_prd_name = self.product_info['product_name']

        self.input_text(self.bl.search, target_prd_name)
        self.press_key(self.bl.search, "Enter")
        self.wait_loaded(self.bl.loading)

        return target_prd_name

    def all_product_selected(self):
        """ 상품 클릭 (홈, 카테고리 사용 가능) """

        # all_product = self.common_data.get_available_product()
        target_prd_id = self.product_info['product_id']
        target_prd_stock = self.product_info['product_stock']
        target_product = self.bl.all_grid(product_id=target_prd_id)

        self.wait_loaded(self.bl.loading)
        self.wait_products_loaded()
        self.get_element_by_locator(target_product).click()

        return {
            "target_product_code" : target_prd_id,
            "target_product_stock" : target_prd_stock
        }