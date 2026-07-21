"""로그인 페이지 ('/login')."""

from __future__ import annotations

from playwright.sync_api import Page, Locator

from locators import LoginLocators
from pages.base_page import BasePage


class LoginPage(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.ll = LoginLocators()

    def go_to_login(self) -> None:
        """홈 헤더의 '로그인' 링크를 클릭해 로그인 페이지로 이동한다."""
        self.get_element_by_locator(self.ll.login_link).click()

    def login(self, username: str, password: str) -> None:
        """아이디/비밀번호를 입력하고 로그인 버튼을 누른다."""
        self.input_text(self.ll.username, username)
        self.input_text(self.ll.password, password)
        self.get_element_by_locator(self.ll.submit).click()

    def auth_user(self) -> Locator:
        """로그인 성공 시 헤더에 노출되는 '{사용자}님' 요소."""
        return self.get_element_by_locator(self.ll.auth_user)

    def error_message(self) -> Locator:
        """로그인 실패 시 노출되는 에러 메시지 요소."""
        return self.get_element_by_locator(self.ll.error)

    def login_card(self) -> Locator:
        """로그인 폼 카드 요소."""
        return self.get_element_by_locator(self.ll.card)

    def logout(self) -> None:
        """헤더의 로그아웃 버튼을 누른다."""
        self.get_element_by_locator(self.ll.logout).click()

    def login_link(self) -> Locator:
        """비로그인 상태에서 헤더에 노출되는 '로그인' 링크 요소."""
        return self.get_element_by_locator(self.ll.login_link)



