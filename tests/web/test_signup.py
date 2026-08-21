"""회원가입 페이지 UI 테스트 (POM 사용).

현재 가입 규칙 기준으로 아래를 검증한다.
- 아이디  : 영문/숫자/특수문자 4~10자
- 비밀번호: 영문/숫자/특수문자 8~16자, 허용 특수문자 1개 이상
- 아이디/비밀번호는 허용 외 문자(한글·공백 등)가 필드에서 걸러져 입력 자체가 되지 않는다
- 비밀번호 확인: 비밀번호와 일치
- 이름    : 1~40자 (문자 제한 없음)
- 연락처  : 3자리-4자리-4자리 하이픈 형식 (예: 010-1234-5678)
- 이메일  : '@' 와 '.' 포함, 최상위도메인 2자 이상, 공백 불가
- 주소    : 1~200자 (문자 제한 없음)
- 중복    : 아이디/이메일/연락처가 이미 사용 중이면 가입 차단

입력 방식은 '직접 입력'과 '붙여넣기' 두 가지로 각각 확인한다.
검증 우선순위: 계정 생성 여부(API 로그인, 1순위) → 페이지 유지/에러 문구(2순위)

차단 케이스는 '가입이 막혔는지' 뿐 아니라 '어느 필드에 어떤 문구가 뜨는지'까지 본다.
기대 문구는 config/ui.json 에서 읽어온다 (Signupdata.msg_value).
"""

import pytest
from pytest import FixtureRequest
from pages.signup.signup_action import Signupaction
from pages.signup.signup_data import Signupdata, ALLOWED_SPECIAL_CHARS, EXISTING_USER
from pages.signup.signup_page import DIRECT, PASTE, SignupPage
from pages.signup.signup_case import filter_cases, invalid_format_cases
from pages.signup.signup_rule import Signuprule
from utilities.api import SignupApi

INPUT_METHODS = [DIRECT, PASTE]


@pytest.mark.ui_journey
class TestSignup():

    @pytest.mark.regression
    @pytest.mark.parametrize("input_method", ["직접입력", "붙여넣기"])
    def test_signup_input_value_match(self, input_method):
        """입력한 값이 각 필드에 그대로 들어간다 (붙여넣기 유실 확인)."""
        signup_page = SignupPage(self.page, self.base_url)
        signup_action = Signupaction(self.page, self.base_url)
        account = Signupdata().valid_account()

        signup_page.go_to_signup()
        signup_action.fill_signup_form(account, input_method)

        assert signup_action.input_value_check(account), f"{input_method} 입력값이 필드에 반영되지 않음"

    # --- 가입 성공 ---
    @pytest.mark.regression
    @pytest.mark.parametrize("input_method", ["직접입력", "붙여넣기"])
    def test_signup_success(self, input_method):
        """모든 규칙을 만족하면 가입이 완료되고 로그인 페이지로 이동한다."""
        signup_page = SignupPage(self.page, self.base_url)
        signup_action = Signupaction(self.page, self.base_url)
        account = Signupdata().valid_account()

        signup_page.go_to_signup()
        signup_action.fill_signup_form(account, input_method)
        assert signup_action.input_value_check(account), f"{input_method} 입력값이 필드에 반영되지 않음"


        signup_page.submit()
        assert signup_action.signup_success_check(account), "정상 정보로 가입되지 않음"



    # --- 아이디 허용 외 문자는 필드에서 걸러진다 ---
    @pytest.mark.regression
    @pytest.mark.parametrize("input_id", filter_cases("username"))
    @pytest.mark.parametrize("input_method", ["직접입력", "붙여넣기"])
    def test_signup_id_disallowed_char_filtered(self, input_id, input_method):
        """아이디/비밀번호에 한글·공백을 넣어도 필드에 남지 않는다 (입력 자체 차단)."""

        signup_page = SignupPage(self.page, self.base_url)
        signup_rule = Signuprule()

        signup_page.go_to_signup()
        signup_page.sign_id_input(input_id, input_method)
        actual = signup_page.field_value("username")

        remained = signup_rule.remove_disallowed(input_id)
        assert actual == remained, f"허용 외 문자가 걸러지지 않음: 입력={input_id!r}, 기대={remained!r}, 실제={actual!r}"


    # --- 비밀번호 허용 외 문자는 필드에서 걸러진다 ---
    @pytest.mark.regression
    @pytest.mark.parametrize("input_pwd", filter_cases("password"))
    @pytest.mark.parametrize("input_method", ["직접입력", "붙여넣기"])
    def test_signup_pwd_disallowed_char_filtered(self, input_pwd, input_method):
        """아이디/비밀번호에 한글·공백을 넣어도 필드에 남지 않는다 (입력 자체 차단)."""

        signup_page = SignupPage(self.page, self.base_url)
        signup_rule = Signuprule()

        signup_page.go_to_signup()
        signup_page.sign_password_input(input_pwd, input_method)
        actual = signup_page.field_value("password")

        remained = signup_rule.remove_disallowed(input_pwd)
        assert actual == remained, f"허용 외 문자가 걸러지지 않음: 입력={input_pwd!r}, 기대={remained!r}, 실제={actual!r}"


    # --- 아이디: 길이 위반 ---
    @pytest.mark.regression
    @pytest.mark.parametrize("invalid_id", invalid_format_cases("username"))
    @pytest.mark.parametrize("input_method", ["직접입력", "붙여넣기"])
    def test_signup_username_invalid(self, invalid_id, input_method):
        """아이디가 길이를 벗어나거나 한글/공백을 포함하면 차단되고 안내 문구가 뜬다."""
        signup_page = SignupPage(self.page, self.base_url)
        signup_action = Signupaction(self.page, self.base_url)
        res = SignupApi(self.api)
        signup_data = Signupdata()

        update_account = signup_data.account_with(username=invalid_id)
        expected_msg = signup_data.msg_value().get("username_length")
        signup_response = res.signup(update_account)

        signup_page.go_to_signup()
        signup_action.fill_signup_form(update_account, input_method)
        signup_page.submit()

        body = signup_response.json()
        target = next(
            (err for err in body.get("detail", []) if "username" in err.get("loc", [])), None
        )

        assert signup_action.signup_blocked_check(update_account, "username", expected_msg), f"허용되지 않는 아이디인데 가입되거나 문구가 다름: {invalid_id!r}"
        assert signup_response.status == 422, "형식 위반인데 가입 api 가 422 가 아님"
        assert target is not None, f"422 응답에 username 오류가 없음: {body}"



    # --- 비밀번호: 길이 위반 / 한글 / 공백 / 특수문자 없음 (차단) ---
    @pytest.mark.regression
    @pytest.mark.parametrize("invalid_pwd", invalid_format_cases("password"))
    @pytest.mark.parametrize("input_method", ["직접입력", "붙여넣기"])
    def test_signup_password_invalid(self, invalid_pwd, input_method, request):
        """비밀번호가 길이/문자 규칙을 어기면 차단되고 안내 문구가 뜬다."""
        case_id = request.node.callspec.id

        signup_page = SignupPage(self.page, self.base_url)
        signup_action = Signupaction(self.page, self.base_url)
        res = SignupApi(self.api)
        signup_data = Signupdata()

        update_account = signup_data.account_with(password=invalid_pwd)

        if "special" in case_id:
            expected_msg = signup_data.msg_value().get("password_no_special")
        else:
            expected_msg = signup_data.msg_value().get("password_length")

        signup_page.go_to_signup()
        signup_action.fill_signup_form(update_account, input_method)

        signup_page.submit()

        signup_response = res.signup(update_account)
        body = signup_response.json()
        target = next(
            (err for err in body.get("detail", []) if "password" in err.get("loc", [])), None
        )

        assert signup_action.signup_blocked_check(update_account, "password", expected_msg), \
            f"허용되지 않는 비밀번호인데 가입되거나 문구가 다름: {invalid_pwd!r}"
        assert signup_response.status == 422, "형식 위반인데 가입 api 가 422 가 아님"
        assert target is not None, f"422 응답에 password 오류가 없음: {body}"









    # @pytest.mark.regression
    # @pytest.mark.parametrize("invalid_id", invalid_format_cases("username"))
    # @pytest.mark.parametrize("input_method", ["직접입력", "붙여넣기"])
    # def test_signup_username_length_boundary(self, invalid_id, input_method):
    #     """아이디가 허용 길이(4자/10자) 경계면 가입된다."""
    #     signup_page = SignupPage(self.page, self.base_url)
    #     signup_rule = Signuprule()
    #     signup_action = Signupaction(self.page, self.base_url)
    #     account = Signupdata().valid_account()
    #     expected_msg = signup_data.msg_value()[msg_key]
    #
    #     signup_page.go_to_signup()
    #     signup_action.fill_signup_form(account, input_method)
    #     account = Signupdata().account_with(username=invalid_id)
    #     signup_page.submit()
    #
    #     assert signup_action.signup_blocked_check(account, "username", expected_msg), \
    #         f"허용되지 않는 아이디인데 가입되거나 문구가 다름: {username!r}"





    # @pytest.mark.regression
    # @pytest.mark.parametrize("input_method", ["직접입력", "붙여넣기"])
    # @pytest.mark.parametrize(
    #     "field, typed, remained",
    #     [
    #         ("username", "테스터01", "01"),
    #         ("username", "qa user", "qauser"),
    #         ("username", "qa01테스터", "qa01"),
    #         ("password", "비밀번호1234!", "1234!"),
    #         ("password", "Pass 123!", "Pass123!"),
    #         ("password_confirm", "Pass 123!", "Pass123!"),
    #     ],
    #     ids=[
    #         "아이디_한글",
    #         "아이디_공백",
    #         "아이디_영문숫자뒤_한글",
    #         "비밀번호_한글",
    #         "비밀번호_공백",
    #         "비밀번호확인_공백",
    #     ],
    # )
    # def test_signup_disallowed_char_filtered(self, field, typed, remained, input_method):
    #     """아이디/비밀번호에 한글·공백을 넣어도 필드에 남지 않는다 (입력 자체 차단)."""
    #     signup_page = SignupPage(self.page, self.base_url)
    #     signup_action = Signupaction(self.page, self.base_url)
    #
    #     signup_page.go_to_signup()
    #     actual = signup_action.fill_field(field, typed, input_method)
    #
    #     assert actual == remained, \
    #         f"{field} 허용 외 문자가 걸러지지 않음: 입력={typed!r}, 기대={remained!r}, 실제={actual!r}"























    # # --- 아이디: 허용 길이 4~10자 (경계값 성공) ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize("input_method", INPUT_METHODS)
    # @pytest.mark.parametrize(
    #     "username",
    #     ["qa01", "qauser0123"],
    #     ids=["아이디_4자", "아이디_10자"],
    # )
    # def test_signup_username_length_boundary(self, username, input_method):
    #     """아이디가 허용 길이(4자/10자) 경계면 가입된다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     account = Signupdata(self.base_url).account_with(username=username)
    #
    #     signup_action.signup(account, input_method)
    #
    #     assert signup_action.signup_success_check(account), f"허용 길이 아이디인데 가입 실패: {username!r}"

    # --- 아이디: 특수문자 허용 (성공) ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize(
    #     "username",
    #     ["qa_01", "qa.user!", "qa-01#"],
    #     ids=["아이디_언더바", "아이디_점_느낌표", "아이디_하이픈_샵"],
    # )
    # def test_signup_username_allows_special_char(self, username):
    #     """아이디는 영문/숫자 외에 허용 특수문자도 쓸 수 있다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     account = Signupdata(self.base_url).account_with(username=username)
    #
    #     signup_action.signup(account)
    #
    #     assert signup_action.signup_success_check(account), f"허용 문자 아이디인데 가입 실패: {username!r}"
    #
    # # --- 아이디: 길이 위반 / 한글 / 공백 (차단) ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize("input_method", INPUT_METHODS)
    # @pytest.mark.parametrize(
    #     "username, msg_key",
    #     [
    #         ("qa1", "username_length"),
    #         ("qauser01234", "username_length"),
    #     ],
    #     ids=["아이디_3자", "아이디_11자"],
    # )
    # def test_signup_username_invalid(self, username, msg_key, input_method):
    #     """아이디가 길이를 벗어나거나 한글/공백을 포함하면 차단되고 안내 문구가 뜬다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     signup_data = Signupdata(self.base_url)
    #     account = signup_data.account_with(username=username)
    #     expected_msg = signup_data.msg_value()[msg_key]
    #
    #     signup_action.signup(account, input_method)
    #
    #     assert signup_action.signup_blocked_check(account, "username", expected_msg), \
    #         f"허용되지 않는 아이디인데 가입되거나 문구가 다름: {username!r}"
    #
    # # --- 비밀번호: 허용 길이 8~16자 (경계값 성공) ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize("input_method", INPUT_METHODS)
    # @pytest.mark.parametrize(
    #     "password",
    #     ["Pass123!", "Passw0rd!Passw0r"],
    #     ids=["비밀번호_8자", "비밀번호_16자"],
    # )
    # def test_signup_password_length_boundary(self, password, input_method):
    #     """비밀번호가 허용 길이(8자/16자) 경계면 가입된다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     account = Signupdata(self.base_url).account_with(password=password)
    #
    #     signup_action.signup(account, input_method)
    #
    #     assert signup_action.signup_success_check(account), f"허용 길이 비밀번호인데 가입 실패: {password!r}"
    #
    # # --- 비밀번호: 길이 위반 / 한글 / 공백 / 특수문자 없음 (차단) ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize("input_method", INPUT_METHODS)
    # @pytest.mark.parametrize(
    #     "password, msg_key",
    #     [
    #         ("Pass12!", "password_length"),
    #         ("Passw0rd!Passw0rd", "password_length"),
    #         ("Password1", "password_no_special"),
    #     ],
    #     ids=["비밀번호_7자", "비밀번호_17자", "비밀번호_특수문자없음"],
    # )
    # def test_signup_password_invalid(self, password, msg_key, input_method):
    #     """비밀번호가 길이/문자 규칙을 어기면 차단되고 안내 문구가 뜬다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     signup_data = Signupdata(self.base_url)
    #     account = signup_data.account_with(password=password)
    #     expected_msg = signup_data.msg_value()[msg_key]
    #
    #     signup_action.signup(account, input_method)
    #
    #     assert signup_action.signup_blocked_check(account, "password", expected_msg), \
    #         f"허용되지 않는 비밀번호인데 가입되거나 문구가 다름: {password!r}"
    #
    # # --- 비밀번호: 허용 특수문자 각각 (성공) ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize("special_char", ALLOWED_SPECIAL_CHARS)
    # def test_signup_password_allowed_special_char(self, special_char):
    #     """허용 특수문자를 하나 포함하면 가입된다. (특수문자별 확인)"""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     account = Signupdata(self.base_url).account_with(password=f"Passw0rd{special_char}")
    #
    #     signup_action.signup(account)
    #
    #     assert signup_action.signup_success_check(account), f"허용 특수문자인데 가입 실패: {special_char!r}"
    #
    # # --- 비밀번호 확인: 불일치 (차단) ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize("input_method", INPUT_METHODS)
    # def test_signup_password_confirm_mismatch(self, input_method):
    #     """비밀번호와 확인값이 다르면 가입이 차단되고 불일치 문구가 노출된다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     signup_data = Signupdata(self.base_url)
    #     account = signup_data.account_with(password_confirm="Passw0rd!!")
    #     mismatch_msg = signup_data.msg_value()["password_mismatch"]
    #
    #     signup_action.signup(account, input_method)
    #
    #     assert signup_action.signup_blocked_check(account, "password_confirm", mismatch_msg), \
    #         "비밀번호 확인이 불일치인데 가입되거나 문구가 노출되지 않음"
    #
    # # --- 이름: 1~40자 ---
    # @pytest.mark.regression
    # def test_signup_name_max_length(self):
    #     """이름이 상한(40자)이면 가입된다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     account = Signupdata(self.base_url).account_with(name="김" * 40)
    #
    #     signup_action.signup(account)
    #
    #     assert signup_action.signup_success_check(account), "이름 40자인데 가입 실패"
    #
    # @pytest.mark.regression
    # def test_signup_name_over_max_length(self):
    #     """이름이 상한을 넘으면(41자) 차단되고 길이 안내 문구가 뜬다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     signup_data = Signupdata(self.base_url)
    #     account = signup_data.account_with(name="김" * 41)
    #     length_msg = signup_data.msg_value()["name_length"]
    #
    #     signup_action.signup(account)
    #
    #     assert signup_action.signup_blocked_check(account, "name", length_msg), \
    #         "이름 41자인데 가입되거나 문구가 노출되지 않음"
    #
    # # --- 연락처: 3-4-4 하이픈 형식만 허용 ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize("input_method", INPUT_METHODS)
    # def test_signup_phone_format(self, input_method):
    #     """연락처가 3-4-4 하이픈 형식이면 가입된다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     account = Signupdata(self.base_url).account_with(phone="010-9876-5432")
    #
    #     signup_action.signup(account, input_method)
    #
    #     assert signup_action.signup_success_check(account), "정상 형식 연락처인데 가입 실패"
    #
    # @pytest.mark.regression
    # @pytest.mark.parametrize("input_method", INPUT_METHODS)
    # @pytest.mark.parametrize(
    #     "phone",
    #     ["01012345678", "010-123-5678", "010-1234-56789", "010-abcd-5678", "010 1234 5678"],
    #     ids=[
    #         "연락처_하이픈없음",
    #         "연락처_가운데자리부족",
    #         "연락처_끝자리초과",
    #         "연락처_문자포함",
    #         "연락처_공백구분",
    #     ],
    # )
    # def test_signup_phone_invalid(self, phone, input_method):
    #     """연락처가 3-4-4 하이픈 형식이 아니면 차단되고 형식 안내 문구가 뜬다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     signup_data = Signupdata(self.base_url)
    #     account = signup_data.account_with(phone=phone)
    #     invalid_msg = signup_data.msg_value()["invalid_phone"]
    #
    #     signup_action.signup(account, input_method)
    #
    #     assert signup_action.signup_blocked_check(account, "phone", invalid_msg), \
    #         f"허용되지 않는 연락처인데 가입되거나 문구가 다름: {phone!r}"
    #
    # # --- 이메일: '@' 와 '.' 포함, 공백 불가 (차단 + 문구) ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize("input_method", INPUT_METHODS)
    # @pytest.mark.parametrize(
    #     "email",
    #     ["qauser01test.com", "qauser01@testcom", "qa user@test.com",
    #      "qauser01@test.c", "qauser01@.com"],
    #     ids=["이메일_골뱅이없음", "이메일_점없음", "이메일_공백포함",
    #          "이메일_최상위도메인_1자", "이메일_도메인없음"],
    # )
    # def test_signup_email_invalid(self, email, input_method):
    #     """이메일 형식이 올바르지 않으면 가입이 차단되고 형식 오류 문구가 노출된다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     signup_data = Signupdata(self.base_url)
    #     account = signup_data.account_with(email=email)
    #     invalid_msg = signup_data.msg_value()["invalid_email"]
    #
    #     signup_action.signup(account, input_method)
    #
    #     assert signup_action.signup_blocked_check(account, "email", invalid_msg), \
    #         f"잘못된 이메일 형식인데 가입되거나 문구가 노출되지 않음: {email!r}"
    #
    # # --- 주소: 1~200자 (문자 제한 없음) ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize("input_method", INPUT_METHODS)
    # @pytest.mark.parametrize(
    #     "address",
    #     ["!@#$%^&*() 101동 202호", "가" * 200],
    #     ids=["주소_특수문자", "주소_200자"],
    # )
    # def test_signup_address_allows_any(self, address, input_method):
    #     """주소는 문자 제한이 없으므로 특수문자/상한 길이여도 가입된다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     account = Signupdata(self.base_url).account_with(address=address)
    #
    #     signup_action.signup(account, input_method)
    #
    #     assert signup_action.signup_success_check(account), f"주소 제한이 없어야 하는데 가입 실패: {address[:20]!r}"
    #
    # @pytest.mark.regression
    # def test_signup_address_over_max_length(self):
    #     """주소가 상한을 넘으면(201자) 차단되고 길이 안내 문구가 뜬다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     signup_data = Signupdata(self.base_url)
    #     account = signup_data.account_with(address="가" * 201)
    #     length_msg = signup_data.msg_value()["address_length"]
    #
    #     signup_action.signup(account)
    #
    #     assert signup_action.signup_blocked_check(account, "address", length_msg), \
    #         "주소 201자인데 가입되거나 문구가 노출되지 않음"
    #
    # # --- 중복 가입 차단 (아이디/이메일/연락처) ---
    # # 서버가 409 로 어느 항목이 중복인지 알려주고, 화면은 그 필드에 문구를 띄운다.
    # @pytest.mark.regression
    # def test_signup_duplicate_username(self):
    #     """이미 사용 중인 아이디면 아이디 필드에 중복 문구가 노출된다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     signup_data = Signupdata(self.base_url)
    #     account = signup_data.account_with(username=EXISTING_USER["username"])
    #     duplicate_msg = signup_data.msg_value()["username_duplicate"]
    #
    #     signup_action.signup(account)
    #
    #     assert signup_action.signup_blocked_check(account, "username", duplicate_msg), \
    #         "중복 아이디인데 가입되거나 문구가 노출되지 않음"
    #
    # @pytest.mark.regression
    # @pytest.mark.parametrize(
    #     "email",
    #     [EXISTING_USER["email"], EXISTING_USER["email"].upper()],
    #     ids=["이메일_중복", "이메일_중복_대문자"],
    # )
    # def test_signup_duplicate_email(self, email):
    #     """이미 사용 중인 이메일이면 이메일 필드에 중복 문구가 노출된다 (대소문자 무관)."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     signup_data = Signupdata(self.base_url)
    #     account = signup_data.account_with(email=email)
    #     duplicate_msg = signup_data.msg_value()["email_duplicate"]
    #
    #     signup_action.signup(account)
    #
    #     assert signup_action.signup_blocked_check(account, "email", duplicate_msg), \
    #         f"중복 이메일인데 가입되거나 문구가 노출되지 않음: {email!r}"
    #
    # @pytest.mark.regression
    # def test_signup_duplicate_phone(self):
    #     """이미 사용 중인 연락처면 연락처 필드에 중복 문구가 노출된다."""
    #     signup_action = Signupaction(self.page, self.base_url)
    #     signup_data = Signupdata(self.base_url)
    #     account = signup_data.account_with(phone=EXISTING_USER["phone"])
    #     duplicate_msg = signup_data.msg_value()["phone_duplicate"]
    #
    #     signup_action.signup(account)
    #
    #     assert signup_action.signup_blocked_check(account, "phone", duplicate_msg), \
    #         "중복 연락처인데 가입되거나 문구가 노출되지 않음"
