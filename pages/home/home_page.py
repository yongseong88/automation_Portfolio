"""홈 페이지 ('/')."""

from __future__ import annotations
from playwright.sync_api import Page, Locator
from locators import BaseLocators, HomeLocators
from pages.base_page import BasePage
from pages.commons.common_action import Commonaction
from pages.commons.common_data import Commondata
from pages.home.home_data import Homedata
from utilities.logger import get_logger

logger = get_logger(__name__)


class HomePage(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.home_data = Homedata(base_url)
        self.common_data = Commondata(base_url)
        self.common_action = Commonaction(self.page, base_url)
        self.hl = HomeLocators()
        self.bl = BaseLocators()

        self.deal_product = self.home_data.get_deal_product()
        self.product_info = self.common_data.get_available_product()

    def deal_product_selected(self):
        """ 특가 상품 클릭 """
        # 2) UI 동작 — 로딩 대기 후 해당 상품 카드 클릭 (미노출/타임아웃 시 대상 id 를 로그로 남김)
        try:
            # 1) 테스트 데이터 추출 — 데이터가 없으면(None) TypeError, 키가 바뀌었으면 KeyError
            try:
                deal_product_code = self.deal_product['product_id']
                deal_product_stock = self.deal_product['product_stock']

            except (KeyError, TypeError):
                # 키 이름/데이터 구조 변경을 바로 알 수 있도록 실제 데이터를 함께 남긴다
                logger.exception("특가 상품 데이터 사용 불가: data=%r", self.deal_product)
                raise

            self.wait_loaded(self.bl.loading)
            self.element_by_click(self.hl.deal_grid(deal_product_code))
            logger.info("특가 상품 클릭 성공: product_id=%s, stock=%s", deal_product_code, deal_product_stock)

            return {
                "target_product_code": deal_product_code,
                "target_product_stock": deal_product_stock
            }

        except Exception:
            logger.exception("특가 상품 클릭 실패: product_id=%s", deal_product_code)
            raise


    def all_product_selected(self):
        """ 전체 상품 클릭 """
        # 2) UI 동작 — 공통 액션(로딩 대기 + 카드 클릭) 위임
        try:
            # 1) 테스트 데이터 추출 — 재고 있는 상품이 없으면 None 이 넘어와 TypeError
            try:
                all_product_code = self.product_info['product_id']
                all_product_stock = self.product_info['product_stock']

            except (KeyError, TypeError):
                logger.exception("상품 데이터 사용 불가: data=%r", self.product_info)
                raise

            self.common_action.all_product_selected(all_product_code)
            logger.info("전체 상품 클릭 성공: product_id=%s", all_product_code)

            return {
                "target_product_code": all_product_code,
                "target_product_stock": all_product_stock
            }

        except Exception:
            logger.exception("전체 상품 클릭 실패: product_id=%s", all_product_code)
            raise



    def valid_product_search(self):
        """ 상품 검색 (홈, 카테고리 사용 가능) """

        # 2) UI 동작 — 검색어 입력 + Enter + 결과 로딩 대기
        #    검색어가 문자열이 아니면 fill() 이 여기서 에러를 내므로 값까지 로그로 남긴다
        try:
            # 1) 검색어 추출 — 데이터 없음(None) → TypeError, 키 변경 → KeyError
            try:
                product_name = self.product_info['product_name']

            except (KeyError, TypeError):
                logger.exception("상품 데이터 사용 불가: data=%r", self.product_info)
                raise

            self.common_action.get_product_search(product_name)
            logger.info("상품 검색 성공: keyword=%s", product_name)
            return product_name

        except Exception:
            logger.exception("상품 검색 실패: keyword=%r", product_name)
            raise

