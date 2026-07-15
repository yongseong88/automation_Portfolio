"""Page Object Model 패키지.

각 페이지의 셀렉터와 동작을 객체로 캡슐화한다.
테스트 코드는 셀렉터를 직접 다루지 않고 페이지 객체의 메서드/로케이터만 사용 → 검증(assert)에만 집중.
"""

from .base_page import BasePage
from pages.home.home_page import HomePage
from pages.category.category_page import CategoryPage
from pages.products.product_page import ProductPage
from pages.cart.cart_page import CartPage
from .cart_api import CartApi
from .login_page import LoginPage
from .auth_api import AuthApi

__all__ = [
    "BasePage",
    "HomePage",
    "CategoryPage",
    "ProductPage",
    "CartPage",
    "CartApi",
    "LoginPage",
    "AuthApi",
]
