"""로그인 페이지 UI 테스트 (POM 사용).

- 성공: 데모 계정으로 로그인 → 홈으로 리다이렉트 + 헤더에 사용자명 노출
- 실패: 잘못된 비밀번호 → 로그인 페이지 유지 + 에러 메시지 노출
- 로그아웃: 로그인 후 로그아웃 → 홈으로 이동 + 비로그인 상태 복귀

검증 우선순위: API status(1순위) → 텍스트/페이지 진입(2순위)
"""

import re
import pytest
from pages import LoginPage
from utilities.api import AuthApi

VALID_ID = "demo"
VALID_PW = "demo1234"


@pytest.mark.ui_journey
class TestLogin():# BaseTest 상속 없이도 됨
    def test_login_success_redirects_and_shows_user(self):
        """올바른 계정으로 로그인하면 홈으로 이동하고 헤더에 '{사용자}님'이 표시된다."""
        login = LoginPage(self.page, self.base_url)
        res = AuthApi(self.api)

        login.go_to_login()  # 홈 → 헤더 '로그인' 버튼 클릭으로 로그인 페이지 진입
        login.login(VALID_ID, VALID_PW)

        login_response = res.login(VALID_ID, VALID_PW)
        print(f"로그인 api 응답: {login_response.status}")

        # 1순위: API status
        assert login_response.status == 200, "로그인 api 호출 실패"
        # 2순위: 페이지 진입 / 텍스트
        login.check_url(f"{self.base_url}/")
        login.check_text(login.auth_user(), f"{VALID_ID}님")

    def test_login_failure_shows_error_and_stays(self):
        """비밀번호가 틀리면 로그인 페이지에 남고 에러 메시지가 표시된다."""
        login = LoginPage(self.page, self.base_url)
        res = AuthApi(self.api)

        login.go_to_login()  # 홈 → 헤더 '로그인' 버튼 클릭으로 로그인 페이지 진입
        login.login(VALID_ID, "wrong-password")

        login_response = res.login(VALID_ID, "wrong-password")
        print(f"로그인 실패 api 응답: {login_response.status}")

        # 1순위: API status (오답 → 401)
        assert login_response.status == 401, "로그인 실패 시 401 이어야 함"
        # 2순위: 에러 텍스트 / 페이지 유지
        login.check_text(login.error_message(), "아이디 또는 비밀번호가 올바르지 않습니다.")
        login.check_url(re.compile(r"/login"))
        login.wait_visible(login.login_card())

    def test_logout_returns_to_guest_state(self):
        """로그인 후 로그아웃하면 홈으로 이동하고 헤더가 비로그인(로그인 링크) 상태로 돌아온다."""
        login = LoginPage(self.page, self.base_url)
        res = AuthApi(self.api)

        login.go_to_login()  # 홈 → 헤더 '로그인' 버튼 클릭으로 로그인 페이지 진입
        login.login(VALID_ID, VALID_PW)
        login.check_text(login.auth_user(), f"{VALID_ID}님")  # 로그인 상태 진입 확인

        login.logout()

        logout_response = res.logout()
        print(f"로그아웃 api 응답: {logout_response.status}")

        # 1순위: API status
        assert logout_response.status == 200, "로그아웃 api 호출 실패"
        # 2순위: 홈 진입 + 비로그인 상태(로그인 링크 노출, 사용자명 사라짐)
        login.check_url(f"{self.base_url}/")
        login.wait_visible(login.login_link())
        login.check_count(login.auth_user(), 0)
