"""로그인 페이지 로케이터."""


class LoginLocators:
    card = '[data-testid="login-card"]'
    username = '[data-testid="login-username"]'
    password = '[data-testid="login-password"]'
    submit = '[data-testid="login-submit"]'
    error = '[data-testid="login-error"]'

    # 로그인 성공 시 헤더 인증 영역에 노출되는 사용자명('{사용자}님')
    auth_user = '[data-testid="auth-user"]'
    # 로그아웃 버튼 / 비로그인 상태의 '로그인' 링크
    logout = '[data-testid="logout"]'
    login_link = '[data-testid="login-link"]'
