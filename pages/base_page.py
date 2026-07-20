"""모든 페이지가 공유하는 기반 클래스.

- 셀렉터 값은 locators/ 의 로케이터 클래스에서 가져온다 (여기엔 동작만).
- 공통 헤더(로고/검색/장바구니/카테고리 네비) 로케이터
- 페이지 진입(open) 및 로딩 스피너 대기(wait_loaded) 같은 공통 동작
- expect() 자동 대기를 활용 → time.sleep 금지
"""

from __future__ import annotations
from playwright.sync_api import Page, Locator, expect
from locators import BaseLocators as L
import logging

logger = logging.getLogger(__name__)

class BasePage:
    # 하위 페이지에서 기본 경로를 지정 (예: "/", "/cart")
    PATH: str = "/"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

        # --- 공통 헤더 ---
        # self.logo: Locator = page.get_by_test_id(L.LOGO)
        # self.search_box: Locator = page.get_by_test_id(L.SEARCH)
        # self.cart_link: Locator = page.get_by_test_id(L.CART_LINK)
        # self.cart_count: Locator = page.get_by_test_id(L.CART_COUNT)
        # self.cat_nav: Locator = page.get_by_test_id(L.CAT_NAV)
        #
        # # 헤더 인증 영역 (로그인 상태에 따라 달라짐)
        # self.auth_user: Locator = page.get_by_test_id(L.AUTH_USER)
        # self.login_link: Locator = page.get_by_test_id(L.LOGIN_LINK)
        # self.logout_btn: Locator = page.get_by_test_id(L.LOGOUT)
        # # 모든 목록형 페이지가 공유하는 로딩 스피너
        # self.loading: Locator = page.get_by_test_id(L.LOADING)

    # --- 공통 동작 ---
    def open(self, path: str | None = None) -> "BasePage":
        """base_url 을 기준으로 절대 URL 을 만들어 이동한다."""
        self.page.goto(f"{self.base_url}{path or self.PATH}")
        # return self


    def get_element_by_id(self, locator: Locator) -> None:
        """요소 클릭. (Playwright 가 클릭 가능 상태까지 자동 대기 후 클릭)"""
        try:
            test_id = self.page.get_by_test_id(locator)
            return test_id

        except Exception:
            logger.exception("요소 찾기 실패: %s", locator)
            raise

    def get_element_by_locator(self, locator: str) -> Locator:
        """요소 클릭. (Playwright 가 클릭 가능 상태까지 자동 대기 후 클릭)"""
        try:
            get_locator = self.page.locator(locator)
            return get_locator

        except Exception:
            logger.exception("click 실패: %s", locator)
            raise

    def is_displayed(self, locator: str, timeout: float = 3000) -> bool:
        """요소가 화면에 보이는지 여부.

        timeout(ms) 동안 나타나기를 기다렸다가, 끝내 안 보이면 False 를 반환한다.
        (스냅샷 is_visible() 과 달리 비동기 렌더링을 견딤 → flaky 방지)
        """
        try:
            expect(locator).to_be_visible(timeout=timeout)
            return True

        except AssertionError:
            return False

    def input_text(self, locator: str, text: str) -> None:
        """텍스트 입력(기존 값을 지우고 새로 채움)."""
        try:
            self.get_element_by_locator(locator).fill(text)
            # self.get_element_by_id(locator).fill(text)

        except Exception:
            logger.exception("input_text 실패: %s", locator)
            raise

    def press_key(self, locator: str, key: str) -> None:
        """키 입력. 예: 'Enter', 'Space', 'Escape', 'Tab'."""
        try:
            self.get_element_by_locator(locator).press(key)
            # self.get_element_by_id(locator).press(key)

        except Exception:
            logger.exception("press_key(%s) 실패: %s", key, locator)
            raise


    def wait_visible(self, locator: str, timeout: float | None = None):
        """요소가 나타날 때까지 대기(동기화). timeout 은 ms, None 이면 기본값."""
        expect(locator).to_be_visible(timeout=timeout)


    def wait_hidden(self, locator: str, timeout: float | None = None):
        """요소가 사라질 때까지 대기(동기화). timeout 은 ms, None 이면 기본값."""
        expect(locator).to_be_hidden(timeout=timeout)


    def wait_loaded(self, locator, timeout: float | None = None):
        """로딩 스피너가 사라질 때까지 대기.

            인자 없이 부르면 공통 스피너(self.loading)를 기다리고,
            페이지마다 다른 로딩 표시가 있으면 그 locator 를 넘긴다.
        """
        loading_spinner = self.get_element_by_locator(locator)
        # self.wait_visible(loading_spinner, timeout)
        self.wait_hidden(loading_spinner, timeout)
        # return self.wait_hidden(locator or self.loading, timeout=timeout)


    # def check_url(self, url) -> None:
    #     """현재 페이지 URL 이 기대값(문자열/정규식)과 일치하는지 검증."""
    #     expect(self.page).to_have_url(url)
    #
    # def check_text(self, locator: Locator, text: str) -> None:
    #     """요소의 텍스트가 기대값과 일치하는지 검증."""
    #     expect(locator).to_have_text(text)

    def check_url(self, url, timeout: float = 3000) -> bool:
        """현재 페이지 URL 이 기대값과 일치하는지 여부.

        테스트에서 assert 로 검증할 때 사용한다.
        timeout(ms) 동안 기다리므로 이동 직후의 레이스를 견딘다 → flaky 방지.
        """
        try:
            expect(self.page).to_have_url(url, timeout=timeout)
            return True

        except AssertionError:
            return False

    def check_text(self, locator: Locator, text: str, timeout: float = 3000) -> bool:
        """요소의 텍스트가 기대값과 일치하는지 여부.

        테스트에서 assert 로 검증할 때 사용한다.
        timeout(ms) 동안 기다리므로 비동기 렌더링을 견딘다 → flaky 방지.
        """
        try:
            expect(locator).to_have_text(text, timeout=timeout)
            return True

        except AssertionError:
            return False

    def check_count(self, locator: Locator, count: int) -> None:
        """요소의 개수가 기대값과 일치하는지 검증 (0 이면 미노출)."""
        expect(locator).to_have_count(count)


    # def open(self, path: str | None = None) -> "BasePage":
    #     """base_url 을 기준으로 절대 URL 을 만들어 이동한다."""
    #     self.page.goto(f"{self.base_url}{path or self.PATH}")
    #     return self
    #
    # def wait_loaded(self) -> "BasePage":
    #     """비동기 상품 로딩(스피너)이 끝날 때까지 대기."""
    #     expect(self.loading).to_be_hidden()
    #     return self
    #
    # def search(self, keyword: str) -> None:
    #     self.search_box.fill(keyword)
    #     self.search_box.press("Enter")
    #
    # def go_to_cart(self) -> None:
    #     self.cart_link.click()

