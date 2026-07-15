"""카테고리 페이지 UI 테스트 (POM 사용)."""

from playwright.sync_api import Page, expect
from pages import CategoryPage
from pages.commons.common_action import Commonaction
from utilities.api import ProductApi
import pytest


@pytest.mark.ui_journey
class TestCategory():# BaseTest 상속 없이도 됨

    def test_category_click(self):
        """카테고리 선택 후 해당 카테고리 상품 목록 API 응답을 검증한다."""
        # category_page = CategoryPage(self.page, self.base_url)
        common_action = Commonaction(self.page, self.base_url)
        res = ProductApi(self.api)

        target_category = common_action.category_selected()

        response = res.products_by_category(target_category)
        print(f"카테고리 상품 목록 api 응답: {response.status}")
        assert response.status == 200, "카테고리 상품 목록 api 호출 실패"

        body = response.json()
        assert "items" in body, "응답 바디에 items 키가 없음"
        assert all(item["category"] == target_category for item in body["items"]), \
            "선택한 카테고리와 다른 상품이 응답에 포함됨"

    def test_sort_default(self):
        """기본순(id 오름차순) 정렬 후 API 응답의 id 정렬 상태를 검증한다."""
        category = CategoryPage(self.page, self.base_url)
        res = ProductApi(self.api)

        target_category = category.default_sort()

        response = res.sort_default(target_category)
        print(f"기본순 api 응답: {response.status}")
        assert response.status == 200, "기본순 api 호출 실패"

        ids = [item["id"] for item in response.json()["items"]]
        assert ids == sorted(ids), "id가 오름차순으로 정렬되지 않음"

    def test_sort_price_low(self):
        """낮은 가격순(가격 오름차순) 정렬 후 API 응답의 가격 정렬 상태를 검증한다."""
        category = CategoryPage(self.page, self.base_url)
        res = ProductApi(self.api)

        target_category = category.price_asc_sort()

        response = res.sort_price_low(target_category)
        print(f"낮은 가격순 api 응답: {response.status}")
        assert response.status == 200, "낮은 가격순 api 호출 실패"

        prices = [item["price"] for item in response.json()["items"]]
        assert prices == sorted(prices), "가격이 오름차순으로 정렬되지 않음"

    def test_sort_price_high(self):
        """높은 가격순(가격 내림차순) 정렬 후 API 응답의 가격 정렬 상태를 검증한다."""
        category = CategoryPage(self.page, self.base_url)
        res = ProductApi(self.api)

        target_category = category.price_desc_sort()

        response = res.sort_price_high(target_category)
        print(f"높은 가격순 api 응답: {response.status}")
        assert response.status == 200, "높은 가격순 api 호출 실패"

        prices = [item["price"] for item in response.json()["items"]]
        assert prices == sorted(prices, reverse=True), "가격이 내림차순으로 정렬되지 않음"

    def test_sort_name(self):
        """이름순(이름 오름차순) 정렬 후 API 응답의 이름 정렬 상태를 검증한다."""
        category = CategoryPage(self.page, self.base_url)
        res = ProductApi(self.api)

        target_category = category.name_asc_sort()

        response = res.sort_name(target_category)
        print(f"이름순 api 응답: {response.status}")
        assert response.status == 200, "이름순 api 호출 실패"

        names = [item["name"] for item in response.json()["items"]]
        assert names == sorted(names), "이름이 오름차순으로 정렬되지 않음"






















        # target_product_id = home.deal_product_selected()
        # product_status = res.product_status(target_product_id)
        # print(f"특가 상품 상세 api 응답: {product_status.status}")
        #
        # assert product_status.status <= 200, "상품 상세 api 호출 실패"


# def test_category_page_shows_only_that_category(page: Page, base_url: str):
#     category = CategoryPage(page, base_url).open("fruits")
#     category.wait_loaded()
#     expect(category.title).to_contain_text("과일")
#     # fruits 시드는 3개
#     expect(category.cards).to_have_count(3)
#
#
# def test_category_sort_low_price_first(page: Page, base_url: str):
#     category = CategoryPage(page, base_url).open("dairy")
#     category.wait_loaded()
#     category.sort_by("price:asc")
#     prices = category.price_values()
#     assert prices == sorted(prices)
