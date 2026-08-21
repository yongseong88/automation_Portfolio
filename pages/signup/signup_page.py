"""
    회원가입 페이지 ('/signup').
    입력/제출 동작과 에러 메시지 접근자를 제공한다.
    - 셀렉터는 SignupLocators 에서만 가져오고, 동작은 base_page 위임 함수로 수행한다.
    - 입력은 '직접 입력'(fill)과 '붙여넣기'(clipboard) 두 방식을 지원한다.
"""
from __future__ import annotations
from playwright.sync_api import Page
from locators import SignupLocators, BaseLocators
from pages import LoginPage
from pages.base_page import BasePage
from utilities.logger import get_logger

logger = get_logger(__name__)

# 입력 방식 구분값 (테스트 파라미터로도 사용)
DIRECT = "직접입력"
PASTE = "붙여넣기"


class SignupPage(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.sl = SignupLocators()
        self.bl = BaseLocators()

        self.login_page = LoginPage(self.page, base_url)

    # --- 진입 ---
    def go_to_signup(self):
        """
            홈 → 헤더 '로그인' → 로그인 페이지의 '회원가입' 링크 클릭으로 진입.
            URL 직접 입력이 아니라 실제 사용자 동선(버튼 클릭)으로 이동한다.
        """

        self.login_page.go_to_login()
        self.login_page.go_to_signup()
        self.signup_form()

    def signup_form(self):
        """회원가입 폼 카드가 노출될 때까지 대기 (페이지 진입 확인)."""
        try:
            self.wait_visible(self.sl.card)

        except Exception:
            logger.exception("회원가입 폼 카드 조회 실패: locator=%s, url=%s", self.sl.card, self.page.url)
            raise

    # --- 입력 ---
    def field_input_value(self, locator, value: str, input_method: str):
        """필드에 값을 입력한다. input_method 로 직접 입력/붙여넣기를 고른다."""
        if input_method == "붙여넣기":
            self.paste_text(locator, value)
        else:
            self.input_text(locator, value)

    def error_locator1(self, field: str) -> str:
        mapping = {
            "username": self.sl.username_error,
            "password": self.sl.password_error,
            "password_confirm": self.sl.password_confirm_error,
            "name": self.sl.name_error,
            "phone": self.sl.phone_error,
            "email": self.sl.email_error,
            "address": self.sl.address_error,
        }

    # 아이디 입력
    def sign_id_input(self, value: str, input_method: str):
        """필드에 값을 입력한다. input_method 로 직접 입력/붙여넣기를 고른다."""
        self.field_input_value(self.sl.username, value, input_method)

    # 아이디 오류 메시지
    def input_id_error_msg(self):
        """아이디 필드의 오류 메시지 텍스트를 반환한다."""
        return self.element_by_msg(self.sl.username_error)

    # 비밀번호 입력
    def sign_password_input(self, value: str, input_method: str):
        """필드에 값을 입력한다. input_method 로 직접 입력/붙여넣기를 고른다."""
        self.field_input_value(self.sl.password, value, input_method)

    # 비밀번호 오류 메시지
    def input_password_error_msg(self):
        """비밀번호 필드의 오류 메시지 텍스트를 반환한다."""
        return self.element_by_msg(self.sl.password_error)

    # 비밀번호 확인 입력
    def sign_passwordconfirm_input(self, value: str, input_method: str):
        """필드에 값을 입력한다. input_method 로 직접 입력/붙여넣기를 고른다."""
        self.field_input_value(self.sl.password_confirm, value, input_method)

    # 비밀번호 확인 오류 메시지
    def input_passwordconfirm_error_msg(self):
        """비밀번호 확인 필드의 오류 메시지 텍스트를 반환한다."""
        return self.element_by_msg(self.sl.password_confirm_error)


    # 이름 입력
    def sign_name_input(self, value: str, input_method: str):
        """필드에 값을 입력한다. input_method 로 직접 입력/붙여넣기를 고른다."""
        self.field_input_value(self.sl.name, value, input_method)

    # 이름 오류 메시지
    def input_name_error_msg(self):
        """이름 필드의 오류 메시지 텍스트를 반환한다."""
        return self.element_by_msg(self.sl.name_error)

    # 핸드폰 번호 입력
    def sign_phone_input(self, value: str, input_method: str):
        """필드에 값을 입력한다. input_method 로 직접 입력/붙여넣기를 고른다."""
        self.field_input_value(self.sl.phone, value, input_method)

    def input_phone_error_msg(self):
        """연락처 필드의 오류 메시지 텍스트를 반환한다."""
        return self.element_by_msg(self.sl.phone_error)


    # 이메일 입력
    def sign_email_input(self, value: str, input_method: str):
        """필드에 값을 입력한다. input_method 로 직접 입력/붙여넣기를 고른다."""
        self.field_input_value(self.sl.email, value, input_method)

    # 이메일 오류 메시지
    def input_email_error_msg(self):
        """이메일 필드의 오류 메시지 텍스트를 반환한다."""
        return self.element_by_msg(self.sl.email_error)


    # 주소 입력
    def sign_address_input(self, value: str, input_method: str):
        """필드에 값을 입력한다. input_method 로 직접 입력/붙여넣기를 고른다."""
        self.field_input_value(self.sl.address, value, input_method)

    # 주소 오류 메시지
    def input_address_error_msg(self):
        """주소 필드의 오류 메시지 텍스트를 반환한다."""
        return self.element_by_msg(self.sl.address_error)



    # 회원 가입 버튼
    def submit(self):
        """'회원가입' 버튼 클릭."""
        self.element_by_click(self.sl.submit)

    def field_value(self, field: str) -> str:
        """입력 필드에 실제로 들어간 값 (붙여넣기가 반영됐는지 확인용)."""
        signup_field = getattr(self.sl, field)
        return self.get_element_by_locator(signup_field).input_value()

    def input_field(self, field: str, value: str, input_method: str = DIRECT):
        """필드에 값을 입력한다. input_method 로 직접 입력/붙여넣기를 고른다."""
        locator = self.input_locator(field)

        if input_method == PASTE:
            self.paste_text(locator, value)
        else:
            self.input_text(locator, value)

    # --- 내부: 필드명 → 로케이터 매핑 ---

    def input_locator(self, field: str) -> str:
        mapping = {
            "username": self.sl.username,
            "password": self.sl.password,
            "password_confirm": self.sl.password_confirm,
            "name": self.sl.name,
            "phone": self.sl.phone,
            "email": self.sl.email,
            "address": self.sl.address,
        }

        return mapping[field]

    def error_locator(self, field: str) -> str:
        mapping = {
            "username": self.sl.username_error,
            "password": self.sl.password_error,
            "password_confirm": self.sl.password_confirm_error,
            "name": self.sl.name_error,
            "phone": self.sl.phone_error,
            "email": self.sl.email_error,
            "address": self.sl.address_error,
        }

        return mapping[field]

    # --- 검증용 접근자 ---
    # def field_value(self, field: str) -> str:
    #     """입력 필드에 실제로 들어간 값 (붙여넣기가 반영됐는지 확인용)."""
    #     return self.get_element_by_locator(self.input_locator(field)).input_value()

    def error_message(self, field: str) -> str:
        """필드별 에러 메시지 텍스트 (없으면 빈 문자열)."""
        return self.element_by_msg(self.error_locator(field))

    def signup_error(self) -> str:
        """폼 전체 에러 메시지 텍스트."""
        return self.element_by_msg(self.sl.signup_error)
