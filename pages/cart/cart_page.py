"""장바구니 페이지 ('/cart')."""

from __future__ import annotations

from playwright.sync_api import Page, Locator
from locators import CartLocators, BaseLocators
from pages.base_page import BasePage
from utilities.logger import get_logger

logger = get_logger(__name__)


class CartPage(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.cl = CartLocators()
        self.bl = BaseLocators()

    def go_to_cart(self):
        """헤더의 장바구니 버튼을 클릭해 장바구니 페이지로 진입 후 로딩 대기."""
        self.element_by_click(self.bl.cart_link)
        self.wait_loaded(self.bl.loading)

    def increase_qty(self, product_code):
        """담긴 첫 상품의 수량(+) 버튼을 눌러 1 증가시키고, 갱신된 수량을 반환한다."""
        item_plus_loc = self.cl.item_plus(product_code)
        self.element_by_click(item_plus_loc)


    def decrease_qty(self, product_code):
        """담긴 첫 상품의 수량(-) 버튼을 눌러 1 감소시키고, 갱신된 수량을 반환한다."""
        item_minus_loc = self.cl.item_minus(product_code)
        self.element_by_click(item_minus_loc)


    def wait_qty(self, product_code, expected_qty) -> bool:
        """화면의 상품 수량이 기대값으로 갱신될 때까지 대기.

        수량 버튼은 '화면에 보이는 수량 +-1' 을 절대값으로 PATCH 한다.
        → 화면 갱신 전에 다음 클릭이 들어가면 같은 값을 두 번 보내 클릭이 유실된다.
        연타할 때는 매 클릭마다 이 대기를 걸어야 한다.
        """
        return self.check_text(self.cl.item_qty(product_code), str(expected_qty))


    def item_remove(self, product_code):
        """담긴 첫 상품의 삭제 버튼을 누르고, 빈 장바구니가 노출될 때까지 대기한다."""

        remove_item_loc = self.cl.item_remove(product_code)
        self.element_by_click(remove_item_loc)
        self.wait_hidden(self.get_element_by_locator(remove_item_loc))

    def go_to_order(self):
        """'주문하기' 버튼을 눌러 주문서(/order)로 이동한다."""
        self.element_by_click(self.cl.checkout)

    # --- 검증용 요소 접근자 ---
    def subtotal(self) -> Locator:
        """상품 합계 금액 요소."""
        return self.get_element_by_locator(self.cl.subtotal)

    def shipping(self, value):
        """
            배송비 금액 요소('무료' 또는 '3,000원').
            화면의 배송비 텍스트를 숫자로 변환. '무료' → 0, '3,000원' → 3000.
            API 의 shipping 값과 바로 비교하기 위한 변환이다.
            (텍스트에 콤마와 '원' 이 붙어 있어 int() 로는 바로 파싱되지 않는다)
        """

        try:
            if value == 0:
                shipping_value = "무료"
            else:
                shipping_value = f"{value:,}원"  # 3000 → "3,000원"

            return self.check_text(self.cl.shipping, shipping_value)

        except Exception:
            logger.exception("배송비 요소 조회 실패: locator=%s", self.cl.shipping)
            raise



        # shipping_text = self.element_by_msg(self.cl.shipping)
        # if "무료" in shipping_text:
        #     return 0
        #
        # return int(shipping_text.replace(",", "").replace("원", "").strip())


    def total(self) -> Locator:
        """최종 결제 금액 요소."""
        return self.get_element_by_locator(self.cl.total)



    def empty(self) -> Locator:
        """빈 장바구니 안내 요소."""
        return self.get_element_by_locator(self.cl.empty)

    def item_qty(self) -> Locator:
        """담긴 첫 상품의 수량 텍스트 요소."""
        return self.get_element_by_locator(self.cl.item_qty).first

