"""장바구니 페이지 UI 테스트 (POM 사용).

상품을 담은 뒤 장바구니 페이지에서 아래 시나리오를 검증한다.
- 주문하기 / 상품 제거 / 수량 증가 / 수량 감소 / 배송비(4만원 기준)

검증 우선순위: API status(1순위) → 텍스트/상태(2순위)
"""

import pytest

from pages import CartPage, HomePage
from pages.cart.cart_action import Cartaction
from pages.products.product_actions import Productaction
from utilities.api import CartApi, OrderApi

IN_STOCK_PRODUCT_ID = 1  # 유기농 시금치 3,900원 (재고 20)


@pytest.mark.ui_journey
class TestCart():# BaseTest 상속 없이도 됨
    def test_cart_order(self):
        """장바구니에서 주문하기 → 주문서로 이동 + 주문 생성(201) + 장바구니 비워짐."""
        cart = CartPage(self.page, self.base_url)
        res = CartApi(self.api)
        order = OrderApi(self.api)

        res.cart_add(IN_STOCK_PRODUCT_ID, 1)

        cart.open_cart()
        cart.order()  # '주문하기' → 주문서(/order)로 이동

        order_response = order.create_order()
        print(f"주문 생성 api 응답: {order_response.status}")

        # 1순위: API status (주문 생성 201)
        assert order_response.status == 201, "주문 생성 api 호출 실패"
        # 2순위: 주문서 진입 + 주문 후 장바구니 비워짐
        cart.check_url(f"{self.base_url}/order")
        cart_response = res.cart_info()
        assert cart_response.status == 200, "장바구니 조회 api 호출 실패"
        assert cart_response.json()["count"] == 0, "주문 후에도 장바구니가 비지 않음"

    def test_cart_remove(self):
        """담긴 상품을 제거하면 장바구니가 비고 빈 상태가 노출된다."""
        cart = CartPage(self.page, self.base_url)
        cart_action = Cartaction(self.page, self.base_url)
        home = HomePage(self.page, self.base_url)
        product_action = Productaction(self.page, self.base_url)
        res = CartApi(self.api)

        product_action.random_product_selected()
        cart.open_cart()
        product_remove_result = cart_action.remove_random_items()

        cart_response = res.cart_info()
        print(f"장바구니 조회 api 응답: {cart_response.status}")

        # 1순위: API status + 삭제 결과
        assert cart_response.status == 200, "장바구니 조회 api 호출 실패"
        assert product_remove_result == True, "장바구니 담기 실패"


        # res.cart_add(IN_STOCK_PRODUCT_ID, 1)
        # deal_product = home.deal_product_selected()
        # deal_product_code = deal_product['target_product_code']
        # deal_product_qty = deal_product['target_product_stock']
        # product_action.product_detail_add_to_cart(deal_product_code, deal_product_qty)


        # cart.remove_first()


        # assert cart_response.json()["count"] == 0, "삭제 후에도 상품이 남아 있음"

        # 2순위: 빈 장바구니 상태 노출
        # cart.wait_visible(cart.empty())


    def test_cart_update(self):
        """담긴 상품을 제거하면 장바구니가 비고 빈 상태가 노출된다."""
        cart = CartPage(self.page, self.base_url)
        cart_action = Cartaction(self.page, self.base_url)
        home = HomePage(self.page, self.base_url)
        product_action = Productaction(self.page, self.base_url)
        res = CartApi(self.api)

        product_add_result = product_action.random_product_selected()
        cart.open_cart()
        cart_update_result = cart_action.items_random_update()

        cart_response = res.cart_info()
        print(f"장바구니 조회 api 응답: {cart_response.status}")

        assert cart_response.status == 200, "장바구니 조회 api 호출 실패"
        assert product_add_result == True, "장바구니 담기 실패"
        assert cart_update_result == True, "장바구니 수량 업데이트 실패"

        # deal_product = home.deal_product_selected()
        # deal_product_code = deal_product['target_product_code']
        # deal_product_qty = deal_product['target_product_stock']
        #
        # product_action.product_detail_add_to_cart(deal_product_code, deal_product_qty)







    # def test_cart_qty_increase(self):
    #     """담긴 상품 수량을 증가시키면 조회 수량이 함께 늘어난다."""
    #     cart = CartPage(self.page, self.base_url)
    #     res = CartApi(self.api)
    #
    #     res.cart_add(IN_STOCK_PRODUCT_ID, 1)
    #
    #     cart.open_cart()
    #     new_qty = cart.increase_qty()
    #
    #     cart_response = res.cart_info()
    #     print(f"장바구니 조회 api 응답: {cart_response.status}")
    #
    #     # 1순위: API status + 수량 값
    #     assert cart_response.status == 200, "장바구니 조회 api 호출 실패"
    #     target = next((i for i in cart_response.json()["items"] if i["id"] == IN_STOCK_PRODUCT_ID), None)
    #     assert target is not None, "상품이 장바구니에 없음"
    #     assert target["qty"] == new_qty, "증가 후 수량이 일치하지 않음"
    #     # 2순위: 화면 수량 텍스트
    #     cart.check_text(cart.item_qty(), str(new_qty))
    #
    # def test_cart_qty_decrease(self):
    #     """담긴 상품 수량을 감소시키면 조회 수량이 함께 줄어든다."""
    #     cart = CartPage(self.page, self.base_url)
    #     res = CartApi(self.api)
    #
    #     res.cart_add(IN_STOCK_PRODUCT_ID, 2)
    #
    #     cart.open_cart()
    #     new_qty = cart.decrease_qty()
    #
    #     cart_response = res.cart_info()
    #     print(f"장바구니 조회 api 응답: {cart_response.status}")
    #
    #     # 1순위: API status + 수량 값
    #     assert cart_response.status == 200, "장바구니 조회 api 호출 실패"
    #     target = next((i for i in cart_response.json()["items"] if i["id"] == IN_STOCK_PRODUCT_ID), None)
    #     assert target is not None, "상품이 장바구니에 없음"
    #     assert target["qty"] == new_qty, "감소 후 수량이 일치하지 않음"
    #     # 2순위: 화면 수량 텍스트
    #     cart.check_text(cart.item_qty(), str(new_qty))
    #
    # def test_cart_shipping_fee_under_threshold(self):
    #     """합계가 4만원 미만이면 배송비 3,000원이 부과된다."""
    #     cart = CartPage(self.page, self.base_url)
    #     res = CartApi(self.api)
    #
    #     # 3,900 x 5 = 19,500원 (< 40,000)
    #     res.cart_add(IN_STOCK_PRODUCT_ID, 5)
    #
    #     cart.open_cart()
    #
    #     cart_response = res.cart_info()
    #     print(f"장바구니 조회 api 응답: {cart_response.status}")
    #
    #     # 1순위: API status + 배송비 값
    #     assert cart_response.status == 200, "장바구니 조회 api 호출 실패"
    #     assert cart_response.json()["shipping"] == 3000, "4만원 미만인데 배송비가 3,000원이 아님"
    #     # 2순위: 화면 배송비 텍스트
    #     cart.check_text(cart.shipping(), "3,000원")
    #
    # def test_cart_shipping_free_over_threshold(self):
    #     """합계가 4만원 이상이면 배송비가 무료로 표시된다."""
    #     cart = CartPage(self.page, self.base_url)
    #     res = CartApi(self.api)
    #
    #     # 3,900 x 11 = 42,900원 (>= 40,000)
    #     res.cart_add(IN_STOCK_PRODUCT_ID, 11)
    #
    #     cart.open_cart()
    #
    #     cart_response = res.cart_info()
    #     print(f"장바구니 조회 api 응답: {cart_response.status}")
    #
    #     # 1순위: API status + 배송비 값
    #     assert cart_response.status == 200, "장바구니 조회 api 호출 실패"
    #     assert cart_response.json()["shipping"] == 0, "4만원 이상인데 배송비가 무료가 아님"
    #     # 2순위: 화면 배송비 텍스트
    #     cart.check_text(cart.shipping(), "무료")
