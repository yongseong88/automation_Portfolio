"""모든 페이지가 공유하는 공통 헤더 로케이터."""


class BaseLocators():
    def all_grid(self, product_id: int):
        all_card_id = f'[data-testid="product-grid"] [data-id="{product_id}"]'
        return all_card_id

    logo = '[data-testid="logo"]'
    card_list = '[data-testid="product-grid"] [data-testid="product-card"]'
    search = '[data-testid="search"]'
    loading = '[data-testid="loading"]'
    cart_link = '[data-testid="cart-link"]'













    # loading = "loading"
    # SEARCH = "search"
    # LOGO = "logo"
    CART_LINK = "cart-link"
    CART_COUNT = "cart-count"
    CAT_NAV = "cat-nav"

    # 헤더 인증 영역 (로그인 상태에 따라 렌더링이 바뀜)
    AUTH_AREA = "auth-area"
    AUTH_USER = "auth-user"
    LOGIN_LINK = "login-link"
    LOGOUT = "logout"
