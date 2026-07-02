"""모든 페이지가 공유하는 기반 클래스.

- 셀렉터 값은 locators/ 의 로케이터 클래스에서 가져온다 (여기엔 동작만).
- 공통 헤더(로고/검색/장바구니/카테고리 네비) 로케이터
- 페이지 진입(open) 및 로딩 스피너 대기(wait_loaded) 같은 공통 동작
- expect() 자동 대기를 활용 → time.sleep 금지
"""

from __future__ import annotations

from playwright.sync_api import Page, Locator, expect

from locators import BaseLocators as L


class BasePage:
    # 하위 페이지에서 기본 경로를 지정 (예: "/", "/cart")
    PATH: str = "/"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

        # --- 공통 헤더 ---
        self.logo: Locator = page.get_by_test_id(L.LOGO)
        self.search_box: Locator = page.get_by_test_id(L.SEARCH)
        self.cart_link: Locator = page.get_by_test_id(L.CART_LINK)
        self.cart_count: Locator = page.get_by_test_id(L.CART_COUNT)
        self.cat_nav: Locator = page.get_by_test_id(L.CAT_NAV)

        # 헤더 인증 영역 (로그인 상태에 따라 달라짐)
        self.auth_user: Locator = page.get_by_test_id(L.AUTH_USER)
        self.login_link: Locator = page.get_by_test_id(L.LOGIN_LINK)
        self.logout_btn: Locator = page.get_by_test_id(L.LOGOUT)
        # 모든 목록형 페이지가 공유하는 로딩 스피너
        self.loading: Locator = page.get_by_test_id(L.LOADING)

    # --- 공통 동작 ---
    def open(self, path: str | None = None) -> "BasePage":
        """base_url 을 기준으로 절대 URL 을 만들어 이동한다."""
        self.page.goto(f"{self.base_url}{path or self.PATH}")
        return self

    def wait_loaded(self) -> "BasePage":
        """비동기 상품 로딩(스피너)이 끝날 때까지 대기."""
        expect(self.loading).to_be_hidden()
        return self

    def search(self, keyword: str) -> None:
        self.search_box.fill(keyword)
        self.search_box.press("Enter")

    def go_to_cart(self) -> None:
        self.cart_link.click()
