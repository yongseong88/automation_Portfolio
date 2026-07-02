"""모든 페이지가 공유하는 공통 헤더 로케이터."""


class BaseLocators:
    LOGO = "logo"
    SEARCH = "search"
    CART_LINK = "cart-link"
    CART_COUNT = "cart-count"
    CAT_NAV = "cat-nav"
    LOADING = "loading"
    # 헤더 인증 영역 (로그인 상태에 따라 렌더링이 바뀜)
    AUTH_AREA = "auth-area"
    AUTH_USER = "auth-user"
    LOGIN_LINK = "login-link"
    LOGOUT = "logout"
