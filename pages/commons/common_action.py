import random

from locators import BaseLocators, CategoryLocators
from pages import BasePage
from playwright.sync_api import Page, Locator
from pages.commons.common_data import Commondata
from utilities.logger import get_logger

logger = get_logger(__name__)

class Commonaction(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.common_data = Commondata(base_url)
        self.bl = BaseLocators()
        self.cl = CategoryLocators()



    def wait_products_loaded(self):
        """상품 카드가 보일 때까지 대기 (홈/카테고리 공용)."""
        try:
            # 카드 목록은 여러 개에 매칭되므로 첫 카드만 대기 (strict mode 위반 방지)
            self.wait_visible(self.bl.card_list, index=0)

        except AssertionError:
            # expect() 타임아웃 → 카드가 끝까지 안 보임 (결과 0건 또는 렌더 실패)
            logger.exception("상품 카드 노출 대기 실패 (결과 0건 또는 렌더 실패): %s", self.bl.card_list)
            raise

        except Exception:
            # 로케이터 자체 오류, 페이지/컨텍스트 종료 등
            logger.exception("상품 카드 로케이터 처리 실패: %s", self.bl.card_list)
            raise

    def logo_selected(self):
        """로고 클릭 → 홈 복귀."""
        try:
            self.element_by_click(self.bl.logo)
            self.wait_loaded(self.bl.loading)

        except Exception:
            logger.exception("로고 클릭/로딩 대기 실패: %s", self.bl.logo)
            raise

        # check_url() 은 bool 을 돌려주므로 assert 로 실패시키고, 사유는 except 에서 로그로 남긴다
        try:
            assert self.check_url(f"{self.base_url}/"), "로고 클릭 후 홈으로 이동하지 않음"

        except AssertionError:
            logger.exception("로고 클릭 후 홈 이동 실패: 현재 URL=%s", self.page.url)
            raise

        self.wait_products_loaded()
        logger.info("로고 클릭 → 홈 복귀 성공")


    def category_selected(self, prd_category):
        """ 카테고리 클릭 (홈, 카테고리 사용 가능) """
        try:
            # 카테고리 값이 비어 있으면 엉뚱한 로케이터가 만들어져 클릭에서 타임아웃 난다
            category_keyword = self.cl.category(prd_category)

            self.wait_products_loaded()
            self.element_by_click(category_keyword)
            self.wait_loaded(self.bl.loading)

        except Exception:
            logger.exception("카테고리 클릭 실패: category=%r, locator=%s", prd_category, self.cl.category(prd_category))
            raise

        logger.info("카테고리 클릭 성공: category=%s", prd_category)

        # API 검증에서 재사용할 수 있도록 선택된 카테고리 slug 반환
        return prd_category

    def get_product_search(self, target_prd_name):
        """ 상품 검색 (홈, 카테고리 사용 가능) """
        try:
            # fill() 은 문자열만 받는다 → 숫자/None 이면 여기서 에러가 나고 값이 로그에 남는다
            self.input_text(self.bl.search, target_prd_name)
            self.press_key(self.bl.search, "Enter")
            self.wait_loaded(self.bl.loading)

        except Exception:
            logger.exception("상품 검색 실패: keyword=%r", target_prd_name)
            raise

        logger.info("상품 검색 성공: keyword=%s", target_prd_name)

        return target_prd_name

    def all_product_selected(self, prd_id):
        """ 상품 클릭 (홈, 카테고리 사용 가능) """
        # 1) 재고 값 추출 — 상품 데이터가 없으면(None) TypeError, 키가 바뀌었으면 KeyError
        # try:
        #     target_prd_stock = self.product_info['product_stock']
        #
        # except (KeyError, TypeError):
        #     logger.exception("상품 데이터 사용 불가: data=%r", self.product_info)
        #     raise

        # 2) UI 동작 — id 가 None 이면 [data-id="None"] 이라 카드를 못 찾고 타임아웃 난다
        try:
            target_product = self.bl.all_grid(product_id=prd_id)

            self.wait_loaded(self.bl.loading)
            self.wait_products_loaded()
            self.element_by_click(target_product)
            logger.info("상품 클릭 성공: product_id=%s", prd_id)

        except Exception:
            logger.exception("상품 클릭 실패: product_id=%r, locator=%s", prd_id, self.bl.all_grid(product_id=prd_id))
            raise



