"""로그인 페이지 UI 테스트 (POM 사용).

- 성공: 데모 계정으로 로그인 → 홈으로 리다이렉트 + 헤더에 사용자명 노출
- 실패: 잘못된 비밀번호 → 로그인 페이지 유지 + 에러 메시지 노출
- 로그아웃: 로그인 후 로그아웃 → 홈으로 이동 + 비로그인 상태 복귀

검증 우선순위: API status(1순위) → 텍스트/페이지 진입(2순위)
"""

import pytest
from pages import LoginPage
from pages.login.login_action import LoginAction
from pages.commons.common_data import Commondata
from utilities.api import AuthApi


@pytest.mark.ui_journey
class TestLogin():# BaseTest 상속 없이도 됨

    @pytest.mark.regression
    def test_login_success_redirects_and_shows_user(self):
        """올바른 계정으로 로그인하면 홈으로 이동하고 헤더에 '{사용자}님'이 표시된다."""
        login_page = LoginPage(self.page, self.base_url)
        login_action = LoginAction(self.page, self.base_url)
        res = AuthApi(self.api)
        account = Commondata(self.base_url).account_config()
        valid_id = account['valid_id']
        valid_pwd = account['valid_pwd']

        login_page.go_to_login()  # 홈 → 헤더 '로그인' 버튼 클릭으로 로그인 페이지 진입
        login_page.set_id(valid_id)
        login_page.set_pwd(valid_pwd)
        login_page.login_submit()

        login_response = res.login(valid_id, valid_pwd)
        print(f"로그인 api 응답: {login_response.status}")

        # 1순위: API status
        assert login_response.status == 200, "로그인 api 호출 실패"

        # 2순위: 페이지 진입 / 텍스트 (홈 이동 + 헤더 '{사용자}님' 노출)
        assert login_action.login_valid_check(valid_id), "로그인 후 홈 이동 또는 사용자명 노출 실패"

    @pytest.mark.regression
    def test_login_failure_shows_error_and_stays(self):
        """비밀번호가 틀리면 로그인 페이지에 남고 에러 메시지가 표시된다."""
        login_page = LoginPage(self.page, self.base_url)
        login_action = LoginAction(self.page, self.base_url)
        res = AuthApi(self.api)
        account = Commondata(self.base_url).account_config()
        valid_id = account['valid_id']
        invalid_pwd = account['invalid_pwd']

        login_page.go_to_login()  # 홈 → 헤더 '로그인' 버튼 클릭으로 로그인 페이지 진입
        login_page.set_id(valid_id)
        login_page.set_pwd(invalid_pwd)
        login_page.login_submit()
        login_page.login_form()

        login_response = res.login(valid_id, invalid_pwd)
        print(f"로그인 실패 api 응답: {login_response.status}")

        login_json = login_response.json()
        login_result_detail = login_json.get("detail", {})

        # 1순위: API status (오답 → 401)
        assert login_response.status == 401, "로그인 실패 시 401 이어야 함"

        # 2순위: 에러 텍스트 / 페이지 유지
        assert login_action.login_valid_check(login_result_detail), "로그인 실패 후 로그인 페이지 유지 또는 에러 메시지 노출 실패"


    @pytest.mark.regression
    def test_logout_returns_to_guest_state(self):
        """로그인 후 로그아웃하면 홈으로 이동하고 헤더가 비로그인(로그인 링크) 상태로 돌아온다."""
        account = Commondata(self.base_url).account_config()
        login_page = LoginPage(self.page, self.base_url)
        login_action = LoginAction(self.page, self.base_url)
        res = AuthApi(self.api)
        valid_id = account['valid_id']
        valid_pwd = account['valid_pwd']
        header_login_status = login_action.msg_value().get("header_login_btn", "")

        login_page.go_to_login()  # 홈 → 헤더 '로그인' 버튼 클릭으로 로그인 페이지 진입
        login_page.set_id(valid_id)
        login_page.set_pwd(valid_pwd)
        login_page.login_submit()

        assert login_action.login_valid_check(valid_id), "로그아웃 전 로그인 상태 진입 실패"

        login_page.logout()
        logout_response = res.logout()
        print(f"로그아웃 api 응답: {logout_response.status}")

        # 1순위: API status
        assert logout_response.status == 200, "로그아웃 api 호출 실패"

        # 2순위: 홈 진입 + 비로그인 상태(로그인 링크 노출, 사용자명 사라짐)
        assert login_action.login_valid_check(header_login_status), "로그아웃 후 홈 이동 또는 비로그인 상태 복귀 실패"
        # login_page.check_count(login_page.auth_user(), 0)
