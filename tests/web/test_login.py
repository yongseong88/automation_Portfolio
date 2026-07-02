"""로그인 페이지 UI 테스트 (POM 사용).

- 성공: 데모 계정으로 로그인 → 홈으로 리다이렉트 + 헤더에 사용자명 노출
- 실패: 잘못된 비밀번호 → 로그인 페이지 유지 + 에러 메시지 노출
"""

import re

from playwright.sync_api import Page, expect

from pages import LoginPage

VALID_ID = "demo"
VALID_PW = "demo1234"


def test_login_success_redirects_and_shows_user(page: Page, base_url: str):
    """올바른 계정으로 로그인하면 홈으로 이동하고 헤더에 '{사용자}님'이 표시된다."""
    login = LoginPage(page, base_url).open()
    login.login(VALID_ID, VALID_PW)

    # 성공 → 홈("/")으로 리다이렉트
    expect(page).to_have_url(f"{base_url}/")
    # 헤더 인증 영역에 로그인 사용자 표시 + 로그아웃 버튼 노출
    expect(login.auth_user).to_have_text(f"{VALID_ID}님")
    expect(login.logout_btn).to_be_visible()


def test_login_failure_shows_error_and_stays(page: Page, base_url: str):
    """비밀번호가 틀리면 로그인 페이지에 남고 에러 메시지가 표시된다."""
    login = LoginPage(page, base_url).open()
    login.login(VALID_ID, "wrong-password")

    # 실패 → 에러 메시지 노출
    expect(login.error).to_have_text("아이디 또는 비밀번호가 올바르지 않습니다.")
    # 페이지 이동 없이 로그인 화면 유지
    expect(page).to_have_url(re.compile(r"/login"))
    expect(login.card).to_be_visible()


def test_logout_returns_to_guest_state(page: Page, base_url: str):
    """로그인 후 로그아웃하면 홈으로 이동하고 헤더가 비로그인(로그인 링크) 상태로 돌아온다."""
    login = LoginPage(page, base_url).open()
    login.login(VALID_ID, VALID_PW)
    expect(login.auth_user).to_have_text(f"{VALID_ID}님")  # 로그인 상태 진입 확인

    login.logout_btn.click()

    # 로그아웃 → 홈으로 이동 + 헤더에 '로그인' 링크가 다시 노출되고 사용자명은 사라짐
    expect(page).to_have_url(f"{base_url}/")
    expect(login.login_link).to_be_visible()
    expect(login.auth_user).to_have_count(0)
