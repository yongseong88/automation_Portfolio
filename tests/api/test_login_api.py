"""로그인 API 테스트 (양성/음성 케이스).

순수 API 자동화 — AuthApi 서비스 래퍼로 검증.
동일한 `api` 컨텍스트를 재사용하므로 로그인 후 세션 쿠키가 다음 요청에 이어진다.
"""

from pages import AuthApi

VALID_ID = "demo"
VALID_PW = "demo1234"


def test_api_login_success_returns_user(api):
    """올바른 계정 → 200 + {"user": {"username": ...}} 스키마."""
    res = AuthApi(api).login(VALID_ID, VALID_PW)
    assert res.status == 200
    body = res.json()
    assert "user" in body
    assert body["user"]["username"] == VALID_ID


def test_api_login_wrong_password_401(api):
    """비밀번호 불일치 → 401."""
    res = AuthApi(api).login(VALID_ID, "nope")
    assert res.status == 401


def test_api_login_unknown_user_401(api):
    """존재하지 않는 계정 → 401."""
    res = AuthApi(api).login("ghost", "whatever")
    assert res.status == 401


def test_api_login_missing_field_422(api):
    """필수 값 누락(빈 비밀번호) → 422 (스키마 검증)."""
    res = AuthApi(api).login(VALID_ID, "")
    assert res.status == 422


def test_api_me_requires_auth_401(api):
    """로그인 전 /api/me 호출 → 401."""
    res = AuthApi(api).me()
    assert res.status == 401


def test_api_login_then_me_returns_username(api):
    """로그인 성공 후 세션 쿠키로 /api/me 조회 → 200 + username 일치."""
    auth = AuthApi(api)
    auth.login(VALID_ID, VALID_PW)
    res = auth.me()
    assert res.status == 200
    assert res.json()["username"] == VALID_ID


def test_api_logout_invalidates_session(api):
    """로그인 → 로그아웃 → 세션 무효화되어 /api/me 가 다시 401."""
    auth = AuthApi(api)
    auth.login(VALID_ID, VALID_PW)
    assert auth.me().status == 200  # 로그인 상태 확인

    res = auth.logout()
    assert res.status == 200
    assert res.json()["ok"] is True

    assert auth.me().status == 401  # 로그아웃 후 인증 해제 확인
