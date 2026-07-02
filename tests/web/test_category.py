"""카테고리 페이지 UI 테스트 (POM 사용)."""

from playwright.sync_api import Page, expect

from pages import CategoryPage


def test_category_page_shows_only_that_category(page: Page, base_url: str):
    category = CategoryPage(page, base_url).open("fruits")
    category.wait_loaded()
    expect(category.title).to_contain_text("과일")
    # fruits 시드는 3개
    expect(category.cards).to_have_count(3)


def test_category_sort_low_price_first(page: Page, base_url: str):
    category = CategoryPage(page, base_url).open("dairy")
    category.wait_loaded()
    category.sort_by("price:asc")
    prices = category.price_values()
    assert prices == sorted(prices)
