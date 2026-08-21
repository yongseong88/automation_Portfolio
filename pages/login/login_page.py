"""로그인 페이지 ('/login')."""

from __future__ import annotations
from playwright.sync_api import Page, Locator
from locators import LoginLocators
from pages.base_page import BasePage
from utilities.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.ll = LoginLocators()

    def login_link(self, login_text):
        """비로그인 상태에서 헤더에 노출되는 '로그인' 링크 요소."""
        try:
            self.wait_visible(self.ll.login_link)
            header_login_btn = self.check_text(self.ll.login_link, login_text)
            if header_login_btn:
                return True

        except Exception:
            logger.exception("로그인 링크 요소 조회 실패: locator=%s", self.ll.login_link)
            raise


    def go_to_login(self) -> None:
        """홈 헤더의 '로그인' 링크를 클릭해 로그인 페이지로 이동한다."""
        try:
            self.wait_visible(self.ll.login_link, 5000)
            self.element_by_click(self.ll.login_link)

            logger.info("로그인 페이지 진입")

            # self.get_element_by_locator(self.ll.login_link).click()

        except Exception:
            # 로그인 링크는 '비로그인 상태'에서만 노출된다 → 이미 로그인된 상태면 못 찾는다
            logger.exception(
                "로그인 링크 클릭 실패 (이미 로그인 상태이거나 헤더 미노출): locator=%s, url=%s",
                self.ll.login_link, self.page.url
            )
            raise

    def go_to_signup(self) -> None:
        """로그인 페이지 하단의 '회원가입' 링크를 클릭해 회원가입 페이지로 이동한다."""
        try:
            self.wait_visible(self.ll.signup_link, 5000)
            self.element_by_click(self.ll.signup_link)

            logger.info("회원가입 페이지 진입")

        except Exception:
            # 회원가입 링크는 로그인 페이지에서만 노출된다 → 다른 페이지면 못 찾는다
            logger.exception(
                "회원가입 링크 클릭 실패 (로그인 페이지가 아니거나 링크 미노출): locator=%s, url=%s",
                self.ll.signup_link, self.page.url
            )
            raise

    def login_form(self):
        """로그인 폼 카드 요소."""
        try:
            self.wait_visible(self.ll.card)

        except Exception:
            logger.exception("로그인 폼 카드 요소 조회 실패: locator=%s", self.ll.card)
            raise

    def set_id(self, username: str):
        try:
            self.wait_visible(self.ll.username, 5000)
            self.input_text(self.ll.username, username)

        except Exception:
            logger.exception("로그인 입력 실패: username=%s", username)
            raise

    def set_pwd(self, password: str):
        try:
            self.wait_visible(self.ll.password, 5000)
            self.input_text(self.ll.password, password)

        except Exception:
            # 비밀번호 값은 로그에 남기지 않는다 (로그 파일/CI 아티팩트 유출 방지)
            logger.exception("비밀번호 입력 실패: locator=%s", self.ll.password)
            raise

    def login_submit(self) -> None:
        """아이디/비밀번호를 입력하고 로그인 버튼을 누른다."""

        try:
            self.wait_visible(self.ll.submit, 5000)
            self.element_by_click(self.ll.submit)

        except Exception:
            logger.exception("로그인 페이지 내 로그인 버튼 클릭 실패: locator=%s", self.ll.submit)
            raise

        # logger.info("로그인 시도 완료: username=%s", username)

    def error_message(self, diff_text):
        """로그인 실패 시 노출되는 에러 메시지 요소."""
        try:
            self.wait_visible(self.ll.error)
            error_msg = self.check_text(self.ll.error, diff_text)
            if error_msg:
                return True

            # return self.get_element_by_locator(self.ll.error)

        except Exception:
            logger.exception("에러 메시지 요소 조회 실패: locator=%s", self.ll.error)
            raise


    def auth_user(self, user_id: str) -> Locator:
        """로그인 성공 시 헤더에 노출되는 '{사용자}님' 요소."""
        try:
            self.wait_visible(self.ll.auth_user)
            header_login_status = self.check_text(self.ll.auth_user, user_id)
            if header_login_status:
                return True
            # return self.get_element_by_locator(self.ll.auth_user)

        except Exception:
            logger.exception("사용자명(auth_user) 요소 조회 실패: locator=%s", self.ll.auth_user)
            raise


    def logout(self) -> None:
        """헤더의 로그아웃 버튼을 누른다."""
        try:
            self.wait_visible(self.ll.logout, 5000)
            self.element_by_click(self.ll.logout)
            # self.get_element_by_locator(self.ll.logout).click()

        except Exception:
            # 로그아웃 버튼은 '로그인 상태'에서만 노출된다 → 로그인 실패/세션 만료면 못 찾는다
            logger.exception(
                "로그아웃 버튼 클릭 실패 (비로그인 상태이거나 버튼 미노출): locator=%s, url=%s",
                self.ll.logout, self.page.url
            )
            raise

        logger.info("로그아웃 완료")