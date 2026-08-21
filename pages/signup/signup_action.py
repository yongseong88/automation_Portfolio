"""회원가입 시나리오 액션.

폼 입력/제출과 결과 검증(가입 성공 / 가입 차단)을 담당한다.
검증은 화면 문구뿐 아니라 '계정이 실제로 만들어졌는지'를 API 로 확인한다.
→ 화면에 에러가 안 떠도 계정이 생겼다면 규칙 위반이므로 실패로 잡는다.
"""

from playwright.sync_api import Page

from locators import SignupLocators
from pages.base_page import BasePage
from pages.login.login_page import LoginPage
from pages.signup.signup_data import Signupdata
from pages.signup.signup_page import SignupPage, DIRECT
from utilities.api import AuthApi
from utilities.logger import get_logger

logger = get_logger(__name__)

# 입력 순서 (화면 배치와 동일)
# FIELDS = ["username", "password", "password_confirm", "name", "phone", "email", "address"]


class Signupaction(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.signup_page = SignupPage(self.page, base_url)
        self.login_page = LoginPage(self.page, base_url)
        self.signup_data = Signupdata()
        self.sl = SignupLocators()

        # 가입 계정으로 실제 로그인이 되는지 확인하기 위한 API (브라우저 세션과 분리)
        self.auth_api = AuthApi(self.page.request)


    # FIELDS = ["username", "password", "password_confirm", "name", "phone", "email", "address"]

    # --- 입력/제출 ---
    def field_inputs(self) -> dict:
        """
            필드명으로 입력 함수를 찾을 수 있게 묶어둔다 (화면 표시 순서).
            괄호 없이 담으므로 함수 자체가 저장되고, 호출부에서 실행한다.
        """
        return {
            "username": self.signup_page.sign_id_input,
            "password": self.signup_page.sign_password_input,
            "password_confirm": self.signup_page.sign_passwordconfirm_input,
            "name":  self.signup_page.sign_name_input,
            "phone": self.signup_page.sign_phone_input,
            "email": self.signup_page.sign_email_input,
            "address": self.signup_page.sign_address_input,
        }

    # --- 오류 메시지 ---
    def field_error_msgs(self) -> dict:
        """
            필드명으로 오류 메시지 조회 함수를 찾을 수 있게 묶어둔다 (화면 표시 순서).
            괄호 없이 담으므로 함수 자체가 저장되고, 호출부에서 실행한다.
            field_inputs 와 같은 키를 쓰므로 field 하나로 입력·검증 양쪽에 접근할 수 있다.
        """
        return {
            "username": self.signup_page.input_id_error_msg,
            "password": self.signup_page.input_password_error_msg,
            "password_confirm": self.signup_page.input_passwordconfirm_error_msg,
            "name": self.signup_page.input_name_error_msg,
            "phone": self.signup_page.input_phone_error_msg,
            "email": self.signup_page.input_email_error_msg,
            "address": self.signup_page.input_address_error_msg,
        }

    def input_field(self, field: str, value: str, input_method: str):
        """특정 필드에 값을 입력한다 (page 의 입력 함수를 골라 실행)."""
        inputs = self.field_inputs()
        action = inputs.get(field)

        if action is None:
            raise KeyError(f"알 수 없는 필드: {field} (사용 가능: {', '.join(inputs)})")

        action(value, input_method)  # 담아둔 함수 실행

    def fill_signup_form(self, account: dict, input_method: str):
        """
            가입 정보 dict 로 폼 전체를 채운다.
            account 에 있는 필드만 입력하므로 일부만 채우는 것도 가능하다.
        """
        for field, action in self.field_inputs().items():
            if field in account:
                action(account.get(field), input_method)

    def get_field_error(self, field: str) -> str:
        """해당 필드의 오류 메시지 텍스트를 반환한다."""
        error_msgs = self.field_error_msgs()
        get_msg = error_msgs.get(field)
        if get_msg is None:
            raise KeyError(f"알 수 없는 필드: {field} (사용 가능: {', '.join(error_msgs)})")

        return get_msg()          # 담아둔 함수 실행


    def account_created(self, account: dict) -> bool:
        """해당 계정으로 로그인이 되는지로 '계정 생성 여부'를 판단한다."""
        response = self.auth_api.login(account.get('username'), account.get('password'))

        return response.status == 200

    def signup_blocked_check(self, account: dict, field: str = "", expected_msg: str = "") -> bool:
        """
            가입 차단 검증: 회원가입 페이지 유지 + 계정 미생성.
            field/expected_msg 를 주면 해당 필드의 에러 문구까지 확인한다.
            규칙은 있으나 화면 문구가 정의되지 않은 경우를 위해 문구 검증은 선택이다.
        """
        try:
            assert self.check_url(f"{self.base_url}/signup"), \
                f"가입 차단 시 회원가입 페이지가 유지되지 않음: 현재={self.page.url}"

            assert not self.account_created(account), \
                f"규칙 위반인데 계정이 생성됨: username={account['username']!r}"

            if field and expected_msg:
                assert self.get_field_error(field) == expected_msg, f"{field} 에러 문구 불일치: 기대={expected_msg!r}, 실제={self.get_field_error(field)!r}"

            logger.info("가입 차단 확인: username=%s field=%s", account.get("username"), field or "-")
            return True

        except AssertionError:
            logger.exception("가입 차단 검증 실패: username=%s", account.get("username"))
            return False

        except Exception:
            logger.exception("가입 차단 검증 중 오류: url=%s", self.page.url)
            raise

    def input_value_check(self, account: dict) -> bool:
        """입력한 값이 화면 필드에 그대로 들어갔는지 검증 (붙여넣기 유실 확인용)."""
        try:
            for field in self.signup_data.field_data():
                actual = self.signup_page.field_value(field)
                assert actual == account.get(field), f"{field} 입력값 불일치: 기대={account[field]!r}, 실제={actual!r}"

            return True

        except AssertionError:
            logger.exception("입력값 불일치: username=%s", account.get('username'))
            return False

        except Exception:
            logger.exception("입력값 확인 중 오류: url=%s", self.page.url)
            raise




















    def signup_with(self, account: dict, input_method: str):
        """폼을 채우고 가입하기까지 수행한다."""
        self.fill_signup_form(account, input_method)
        self.signup_page.click_submit()





























    def fill_form(self, account: dict, input_method: str):
        """가입 폼 전체를 채운다. input_method: 직접입력 / 붙여넣기."""


        self.signup_page.sign_id_input(account.get('username'), input_method)
        self.signup_page.sign_password_input(account.get('password'), input_method)
        self.signup_page.sign_passwordconfirm_input(account.get('password_confirm'), input_method)
        self.signup_page.sign_name_input(account.get('name'), input_method)
        self.signup_page.sign_phone_input(account.get('phone'), input_method)
        self.signup_page.sign_email_input(account.get('email'), input_method)
        self.signup_page.sign_address_input(account.get('address'), input_method)

        # for field in self.FIELDS:
        #     self.signup_page.input_field(field, account[field], input_method)
        #
        # logger.info("가입 폼 입력 완료: username=%s 방식=%s", account["username"], input_method)

    def fill_field(self, field: str, value: str, input_method: str = DIRECT) -> str:
        """
            한 필드만 입력하고, 화면에 실제로 남은 값을 돌려준다.
            아이디/비밀번호는 허용되지 않는 문자가 필드에서 걸러지므로
            '입력한 값'과 '남은 값'이 다를 수 있다.
        """
        self.signup_page.input_field(field, value, input_method)

        return self.signup_page.field_value(field)

    def signup(self, account: dict, input_method: str = DIRECT):
        """회원가입 페이지 진입 → 폼 입력 → 제출."""
        self.signup_page.go_to_signup()
        self.fill_form(account, input_method)
        self.signup_page.submit()

    # --- 결과 검증 ---
    def signup_success_check(self, account: dict) -> bool:
        """가입 성공 검증: 로그인 페이지로 이동 + 생성된 계정으로 로그인 가능."""
        try:
            # 성공 시 토스트 노출 후 /login 으로 이동한다
            assert self.check_url(f"{self.base_url}/login"), f"가입 성공 후 로그인 페이지로 이동하지 않음: 현재={self.page.url}"
            assert self.account_created(account), f"가입은 됐다는데 해당 계정으로 로그인되지 않음: username={account.get('username')}"

        except AssertionError:
            logger.exception("가입 성공 검증 실패: username=%s", account.get('username'))
            return False

        except Exception:
            logger.exception("가입 성공 검증 중 오류: url=%s", self.page.url)
            raise

        logger.info("가입 성공: username=%s", account.get('username'))

        return True




























    # def signup_blocked_check(self, account: dict, field: str = "", expected_msg: str = "") -> bool:
    #     """
    #         가입 차단 검증: 회원가입 페이지 유지 + 계정 미생성.
    #         field/expected_msg 를 주면 해당 필드의 에러 문구까지 확인한다.
    #         규칙은 있으나 화면 문구가 정의되지 않은 경우를 위해 문구 검증은 선택이다.
    #     """
    #     try:
    #         assert self.check_url(f"{self.base_url}/signup"), \
    #             f"가입 차단 시 회원가입 페이지가 유지되지 않음: 현재={self.page.url}"
    #
    #         assert not self.account_created(account), \
    #             f"규칙 위반인데 계정이 생성됨: username={account['username']!r}"
    #
    #         if field and expected_msg:
    #             assert self.check_text(self.signup_page.error_locator(field), expected_msg), \
    #                 f"{field} 에러 문구 불일치: 기대={expected_msg!r}, 실제={self.signup_page.error_message(field)!r}"
    #
    #         logger.info("가입 차단 확인: username=%s field=%s", account["username"], field or "-")
    #         return True
    #
    #     except AssertionError:
    #         logger.exception("가입 차단 검증 실패: username=%s", account["username"])
    #         return False
    #
    #     except Exception:
    #         logger.exception("가입 차단 검증 중 오류: url=%s", self.page.url)
    #         raise




