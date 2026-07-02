"""로케이터(셀렉터) 패키지.

화면의 data-testid 값을 페이지별 클래스로 모아둔다.
- 페이지 동작(pages/)과 셀렉터를 분리 → 화면이 바뀌면 여기만 수정한다.
- 각 클래스는 testid '문자열'만 보관하고, 실제 Locator 생성은 페이지 클래스가 담당한다.
"""

from .base_locators import BaseLocators
from .home_locators import HomeLocators
from .category_locators import CategoryLocators
from .product_locators import ProductLocators
from .cart_locators import CartLocators
from .login_locators import LoginLocators

__all__ = [
    "BaseLocators",
    "HomeLocators",
    "CategoryLocators",
    "ProductLocators",
    "CartLocators",
    "LoginLocators",
]
