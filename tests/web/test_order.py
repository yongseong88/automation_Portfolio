"""주문서 페이지 UI 테스트 (POM 사용).

장바구니에 상품을 담아 주문서('/order')로 진입한 뒤 아래 시나리오를 검증한다.
- 주문 성공 (결제수단 card/bank/easy 별로 확인)
- 주문 실패 (이름/연락처/이메일 미입력, 이메일 형식 오류)
- 주문 상품/가격 일치 확인
- 페이지 이동 확인 (성공 → 완료 페이지, 실패 → 현재 페이지 유지)

검증 우선순위: API status(1순위) → 텍스트/상태(2순위)
주문 성공 검증은 POST /api/orders(201) 가 아니라, 완료 후 GET /api/orders/{id}(200) 로 확인한다.
"""

import re
import pytest
from pages import OrderPage, CartPage
from pages.cart.cart_action import Cartaction
from pages.order.order_action import Orderaction
from pages.products.product_actions import Productaction
from utilities.api import CartApi, OrderApi

IN_STOCK_PRODUCT_ID = 1  # 유기농 시금치 3,900원 (재고 20)

# 프론트(validate) 가 노출하는 에러 문구
ERR_REQUIRED = "필수 입력 항목입니다."
ERR_EMAIL = "이메일 형식이 올바르지 않습니다."


@pytest.mark.ui_journey
class TestOrder():# BaseTest 상속 없이도 됨

    ORDERER = {"name": "홍길동", "phone": "010-1234-5678", "email": "crosswindy@naver.com"}
    DELIVERY = {"recipient": "김수령", "phone": "010-8765-4321", "address": "서울시 강남구 테헤란로 1"}

    # --- 공통 준비/입력 헬퍼 ---
    def _open_order_with_item(self) -> OrderPage:
        """카트에 상품을 담고(전역 카트) 주문서로 진입한다."""
        add_response = CartApi(self.api).cart_add(IN_STOCK_PRODUCT_ID, 1)
        assert add_response.status == 200, "사전 준비(장바구니 담기) 실패"

        order_page = OrderPage(self.page, self.base_url)
        order_page.open_order()
        return order_page

    def _fill_valid(self, order_page: OrderPage, payment: str = "card"):
        """유효한 값으로 주문서 전체를 채우고 결제수단을 선택한다."""
        order_page.fill_orderer(**self.ORDERER)
        order_page.fill_delivery(**self.DELIVERY)
        order_page.select_payment(payment)

    # --- 주문 성공: 결제수단별 ---
    @pytest.mark.regression
    @pytest.mark.parametrize("payment", ["card", "bank", "easy"])
    def test_order_success(self, payment):
        """결제수단별로 주문이 성공하고, 완료 페이지 진입 + 상품/가격이 일치한다."""

        cart_page = CartPage(self.page, self.base_url)
        order_page = OrderPage(self.page, self.base_url)
        order_action = Orderaction(self.page, self.base_url)
        product_action = Productaction(self.page, self.base_url)
        order_api = OrderApi(self.api)

        cart_add_result = product_action.random_product_selected()
        assert cart_add_result, "장바구니 담기 실패"

        cart_page.open_cart()
        cart_page.order()
        checkout = order_api.checkout_info().json()  # 주문 직전 스냅샷(상품/금액)
        order_action.fill_orderer()
        order_action.fill_delivery()
        order_page.select_payment(payment)
        order_page.place_order()

        # 페이지 이동: 성공 → 주문 완료 페이지
        assert order_page.check_url(re.compile(rf"{re.escape(self.base_url)}/order/complete/\d+")), \
            "주문 성공 후 주문 완료 페이지로 이동하지 않음"
        order_page.complete_container()
        order_id = order_page.order_id_from_url()

        # 1순위: 주문 조회 GET 200 (POST 201 아님)
        order_response = order_api.get_order(order_id)
        print(f"주문 조회 api 응답: {order_response.status}")
        ordered = order_response.json()

        # api 응답값 일치 확인
        assert order_response.status == 200, "주문 조회 api 응답이 200이 아님"
        # 주문 상품 일치
        assert [i["id"] for i in ordered["items"]] == [i["id"] for i in checkout["items"]], "주문 상품이 장바구니와 불일치"
        # 주문 가격 일치
        assert ordered["total"] == checkout["total"], "주문 결제금액이 장바구니와 불일치"

    # --- 주문 실패: 필수값 미입력 (이름/연락처/이메일) ---
    @pytest.mark.regression
    @pytest.mark.parametrize("field", ["orderer_name", "orderer_phone", "orderer_email", "recipient", "reciver_phone", "address"])
    def test_order_fail_missing_required(self, field):
        """필수 항목을 비우면 주문이 차단되고 현재 페이지가 유지되며 에러가 노출된다."""

        cart_page = CartPage(self.page, self.base_url)
        order_page = OrderPage(self.page, self.base_url)
        order_action = Orderaction(self.page, self.base_url)
        product_action = Productaction(self.page, self.base_url)
        order_api = OrderApi(self.api)

        cart_add_result = product_action.random_product_selected()
        assert cart_add_result, "장바구니 담기 실패"

        cart_page.open_cart()
        cart_page.order()
        order_action.fill_orderer()
        order_action.fill_delivery()

        order_page.clear_field(field)  # 해당 항목만 비움
        order_page.place_order()

        # 페이지 이동: 실패 → 현재(/order) 유지
        assert order_page.check_url(f"{self.base_url}/order"), "주문 실패 후 주문서 페이지가 유지되지 않음"

        # 에러 노출
        assert order_page.check_text(order_page.error(field), ERR_REQUIRED), f"{field} 필수 입력 에러 문구가 노출되지 않음"

    # # --- 주문 실패: 이메일 형식 오류 (@ 누락 / 도메인 형식 오류) ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize("bad_email", ["crosswindynavercom", "crosswindy@navercom"])
    # def test_order_fail_invalid_email(self, bad_email):
    #     """이메일 형식이 올바르지 않으면 주문이 차단되고 현재 페이지가 유지된다."""
    #     order_page = self._open_order_with_item()
    #     self._fill_valid(order_page)
    #     order_page.set_field("orderer_email", bad_email)
    #
    #     order_page.place_order()
    #
    #     # 페이지 이동: 실패 → 현재(/order) 유지
    #     order_page.check_url(f"{self.base_url}/order")
    #     # 에러 노출
    #     order_page.check_text(order_page.error("orderer_email"), ERR_EMAIL)











    # --- 주문 성공: 결제수단별 ---
    # @pytest.mark.regression
    # @pytest.mark.parametrize("payment", ["card", "bank", "easy"])
    # def test_order_success_by_payment(self, payment):
    #     """결제수단별로 주문이 성공하고, 완료 페이지 진입 + 상품/가격이 일치한다."""
    #     order_page = self._open_order_with_item()
    #     order_api = OrderApi(self.api)
    #     checkout = order_api.checkout_info().json()  # 주문 전 스냅샷(상품/금액)
    #
    #     self._fill_valid(order_page, payment)
    #     order_page.place_order()
    #
    #     # 페이지 이동: 성공 → 주문 완료 페이지
    #     order_page.check_url(re.compile(rf"{re.escape(self.base_url)}/order/complete/\d+"))
    #     order_page.wait_visible(order_page.complete_container())
    #     order_id = order_page.order_id_from_url()
    #
    #     # 1순위: 주문 조회 GET 200 (POST 201 아님)
    #     order_response = order_api.get_order(order_id)
    #     print(f"주문 조회 api 응답: {order_response.status}")
    #     assert order_response.status == 200, "주문 조회 api 응답이 200이 아님"
    #
    #     ordered = order_response.json()
    #
    #     # 주문 상품 일치
    #     assert [i["id"] for i in ordered["items"]] == [i["id"] for i in checkout["items"]], \
    #         "주문 상품이 장바구니와 불일치"
    #
    #     # 주문 가격 일치
    #     assert ordered["total"] == checkout["total"], "주문 결제금액이 장바구니와 불일치"
    #
    # # --- 주문 상품 일치 (단독 케이스) ---
    # @pytest.mark.regression
    # def test_ordered_items_match(self):
    #     """주문 완료 후 주문 상품이 주문 직전 장바구니와 동일하다."""
    #     order_page = self._open_order_with_item()
    #     order_api = OrderApi(self.api)
    #     checkout = order_api.checkout_info().json()
    #
    #     self._fill_valid(order_page)
    #     order_page.place_order()
    #     order_page.check_url(re.compile(rf"{re.escape(self.base_url)}/order/complete/\d+"))
    #
    #     order_response = order_api.get_order(order_page.order_id_from_url())
    #     assert order_response.status == 200, "주문 조회 api 응답이 200이 아님"
    #     assert [i["id"] for i in order_response.json()["items"]] == \
    #         [i["id"] for i in checkout["items"]], "주문 상품이 장바구니와 불일치"
    #
    # # --- 주문 가격 일치 (단독 케이스) ---
    # @pytest.mark.regression
    # def test_ordered_price_match(self):
    #     """주문 완료 후 결제금액이 주문 직전 장바구니 총액과 동일하다."""
    #     order_page = self._open_order_with_item()
    #     order_api = OrderApi(self.api)
    #     checkout = order_api.checkout_info().json()
    #
    #     self._fill_valid(order_page)
    #     order_page.place_order()
    #     order_page.check_url(re.compile(rf"{re.escape(self.base_url)}/order/complete/\d+"))
    #
    #     order_response = order_api.get_order(order_page.order_id_from_url())
    #     assert order_response.status == 200, "주문 조회 api 응답이 200이 아님"
    #     assert order_response.json()["total"] == checkout["total"], \
    #         "주문 결제금액이 장바구니와 불일치"
    #

    #

