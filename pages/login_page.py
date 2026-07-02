"""로그인 페이지 ('/login')."""

from __future__ import annotations

from playwright.sync_api import Page, Locator

from locators import LoginLocators as L
from .base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.card: Locator = page.get_by_test_id(L.CARD)
        self.username: Locator = page.get_by_test_id(L.USERNAME)
        self.password: Locator = page.get_by_test_id(L.PASSWORD)
        self.submit_btn: Locator = page.get_by_test_id(L.SUBMIT)
        self.error: Locator = page.get_by_test_id(L.ERROR)

    def login(self, username: str, password: str) -> "LoginPage":
        """아이디/비밀번호를 입력하고 로그인 버튼을 누른다."""
        self.username.fill(username)
        self.password.fill(password)
        self.submit_btn.click()
        return self
