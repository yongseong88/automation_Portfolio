"""회원가입 페이지 ('/signup') 로케이터."""


class SignupLocators:

    card = '[data-testid="signup-card"]'

    # --- 입력 필드 ---
    username = '[data-testid="signup-username"]'
    password = '[data-testid="signup-password"]'
    password_confirm = '[data-testid="signup-password-confirm"]'
    name = '[data-testid="signup-name"]'
    phone = '[data-testid="signup-phone"]'
    email = '[data-testid="signup-email"]'
    address = '[data-testid="signup-address"]'

    # --- 필드별 에러 메시지 ---
    username_error = '[data-testid="username-error"]'
    password_error = '[data-testid="password-error"]'
    password_confirm_error = '[data-testid="password-confirm-error"]'
    name_error = '[data-testid="name-error"]'
    phone_error = '[data-testid="phone-error"]'
    email_error = '[data-testid="email-error"]'
    address_error = '[data-testid="address-error"]'

    # --- 제출 / 전체 에러 ---
    submit = '[data-testid="signup-submit"]'
    signup_error = '[data-testid="signup-error"]'
    go_login = '[data-testid="go-login"]'
