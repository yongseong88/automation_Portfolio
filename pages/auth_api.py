"""인증(로그인) API 서비스 래퍼.

UI 테스트에서 세션을 빠르게 준비하거나, 순수 API 테스트에서 사용한다.
Playwright APIRequestContext 를 감싸 인증 엔드포인트/페이로드를 한 곳에 모은다.
동일 컨텍스트를 재사용하면 로그인 후 세션 쿠키가 다음 요청에 자동으로 실린다.
"""

from __future__ import annotations

from playwright.sync_api import APIRequestContext, APIResponse


class AuthApi:
    def __init__(self, request: APIRequestContext):
        self.request = request

    def login(self, username: str, password: str) -> APIResponse:
        return self.request.post(
            "/api/login", data={"username": username, "password": password}
        )

    def me(self) -> APIResponse:
        return self.request.get("/api/me")

    def logout(self) -> APIResponse:
        return self.request.post("/api/logout")
