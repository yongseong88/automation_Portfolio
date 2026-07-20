"""장바구니 페이지 ('/cart')."""

from __future__ import annotations

from playwright.sync_api import Page, Locator
from locators import CartLocators, BaseLocators
from pages.base_page import BasePage


class CartPage(BasePage):
    PATH = "/cart"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.cl = CartLocators()
        self.bl = BaseLocators()

    def open_cart(self):
        """헤더의 장바구니 버튼을 클릭해 장바구니 페이지로 진입 후 로딩 대기."""
        self.get_element_by_locator(self.bl.cart_link).click()
        self.wait_loaded(self.bl.loading)

    def increase_qty(self, product_code, count) -> int:
        """담긴 첫 상품의 수량(+) 버튼을 눌러 1 증가시키고, 갱신된 수량을 반환한다."""

        item_plus_loc = self.cl.item_plus(product_code)
        item_qty_loc = self.cl.item_qty(product_code)

        plus_el = self.get_element_by_locator(item_plus_loc)
        qty_el = self.get_element_by_locator(item_qty_loc)

        current = int(qty_el.inner_text())  # 수량 직접 읽기

        for _ in range(count):
            current += 1
            plus_el.click()
            assert self.check_text(qty_el, str(current)), f"수량 증가 후 화면 수량이 {current} 로 갱신되지 않음"

        return current


        # qty_el = self.get_element_by_locator(self.cl.item_qty).first
        # new_qty = int(qty_el.inner_text()) + 1
        # self.get_element_by_locator(self.cl.item_plus).first.click()
        # self.check_text(qty_el, str(new_qty))  # UI(=서버) 반영 대기
        # return new_qty

    def decrease_qty(self, product_code, count) -> int:
        """담긴 첫 상품의 수량(-) 버튼을 눌러 1 감소시키고, 갱신된 수량을 반환한다."""

        item_minus_loc = self.cl.item_minus(product_code)
        item_qty_loc = self.cl.item_qty(product_code)

        minus_el = self.get_element_by_locator(item_minus_loc)
        qty_el = self.get_element_by_locator(item_qty_loc)

        current = int(qty_el.inner_text())  # 수량 직접 읽기

        for _ in range(count):
            current -= 1
            minus_el.click()
            assert self.check_text(qty_el, str(current)), f"수량 감소 후 화면 수량이 {current} 로 갱신되지 않음"

        return current

        # qty_el = self.get_element_by_locator(self.cl.item_qty).first
        # new_qty = int(qty_el.inner_text()) - 1
        # self.get_element_by_locator(self.cl.item_minus).first.click()
        # self.check_text(qty_el, str(new_qty))  # UI(=서버) 반영 대기
        # return new_qty

    def item_remove(self, product_code):
        """담긴 첫 상품의 삭제 버튼을 누르고, 빈 장바구니가 노출될 때까지 대기한다."""

        remove_item_loc = self.cl.item_remove(product_code)

        self.get_element_by_locator(remove_item_loc).click()
        self.wait_hidden(self.get_element_by_locator(remove_item_loc))
        # self.wait_visible(self.get_element_by_locator(self.cl.empty))

    def order(self):
        """'주문하기' 버튼을 눌러 주문서(/order)로 이동한다."""
        self.get_element_by_locator(self.cl.checkout).click()

    # --- 검증용 요소 접근자 ---
    def empty(self) -> Locator:
        """빈 장바구니 안내 요소."""
        return self.get_element_by_locator(self.cl.empty)

    def item_qty(self) -> Locator:
        """담긴 첫 상품의 수량 텍스트 요소."""
        return self.get_element_by_locator(self.cl.item_qty).first

    def subtotal(self) -> Locator:
        """상품 합계 금액 요소."""
        return self.get_element_by_locator(self.cl.subtotal)

    def shipping(self) -> Locator:
        """배송비 금액 요소('무료' 또는 '3,000원')."""
        return self.get_element_by_locator(self.cl.shipping)

    def total(self) -> Locator:
        """최종 결제 금액 요소."""
        return self.get_element_by_locator(self.cl.total)
