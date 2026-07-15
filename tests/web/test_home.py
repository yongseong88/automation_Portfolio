"""홈 페이지 UI 테스트 (POM 사용)."""
from playwright.sync_api import Page, expect
from pages import HomePage
from pages.commons.common_action import Commonaction
from utilities.api import ProductApi
import pytest

@pytest.mark.ui_journey
class TestHome():# BaseTest 상속 없이도 됨
    def test_home_deal_product_click(self):
        home = HomePage(self.page, self.base_url)
        res = ProductApi(self.api)

        target_product_id = home.deal_product_selected()['target_product_code']
        product_status = res.product_detail(target_product_id)
        print(f"특가 상품 상세 api 응답: {product_status.status}")

        assert product_status.status <= 200, "상품 상세 api 호출 실패"

    def test_home_all_product_click(self):
        home = HomePage(self.page, self.base_url)
        res = ProductApi(self.api)

        target_product_id = home.all_product_selected()['target_product_code']
        product_status = res.product_detail(target_product_id)
        print(f"전체 상품 상세 api 응답: {product_status.status}")

        assert product_status.status <= 200, "상품 상세 api 호출 실패"


    def test_home_product_search(self):
        common_action = Commonaction(self.page, self.base_url)
        res = ProductApi(self.api)

        search_name = common_action.product_search()
        search_product_name = res.search_query(search_name)
        print(f"상품 검색 api 응답: {search_product_name.status}")

        assert search_product_name.status <= 200, "검색 api 호출 실패"


    # def test_home_loads_products(page: Page, base_url: str):
    #     home = HomePage(page, base_url).open()
    #     home.wait_loaded()
    #     # 홈에는 카드가 '전체 상품'+'특가' 두 곳에 있으므로 그리드 범위를 한정해서 센다
    #     expect(home.cards.first).to_be_visible()
    #     expect(home.cards).to_have_count(16)
    #
    #
    # def test_home_has_deal_section(page: Page, base_url: str):
    #     home = HomePage(page, base_url).open()
    #     home.wait_loaded()
    #     expect(home.deal_cards.first).to_be_visible()
    #
    #
    # def test_search_filters_and_shows_count(page: Page, base_url: str):
    #     home = HomePage(page, base_url).open()
    #     home.search("딸기")
    #     expect(home.search_title).to_contain_text("검색 결과")
    #     expect(home.cards).to_have_count(1)
