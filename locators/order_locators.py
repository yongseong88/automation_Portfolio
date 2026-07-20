"""주문서('/order') 및 주문 완료('/order/complete/{id}') 페이지 로케이터."""


class OrderLocators:

    # --- 주문자 정보 입력 ---
    orderer_name = '[data-testid="orderer-name"]'
    orderer_phone = '[data-testid="orderer-phone"]'
    orderer_email = '[data-testid="orderer-email"]'

    # --- 주문자 정보 에러 메시지 ---
    orderer_name_error = '[data-testid="orderer-name-error"]'
    orderer_phone_error = '[data-testid="orderer-phone-error"]'
    orderer_email_error = '[data-testid="orderer-email-error"]'

    # --- 배송지 정보 입력 ---
    recipient = '[data-testid="order-recipient"]'
    phone = '[data-testid="order-phone"]'
    address = '[data-testid="order-address"]'
    request = '[data-testid="order-request"]'

    # --- 배송지 정보 에러 메시지 ---
    recipient_error = '[data-testid="recipient-error"]'
    reciver_phone_error = '[data-testid="phone-error"]'
    address_error = '[data-testid="address-error"]'

    # --- 결제수단 (card / bank / easy) ---
    def pay(self, method: str):
        pay_loc = f'[data-testid="pay-{method}"]'
        return pay_loc

    # --- 주문 상품 / 금액 / 제출 ---
    order_items = '[data-testid="order-items"]'
    order_item = '[data-testid="order-item"]'
    order_total = '[data-testid="order-total"]'
    place_order = '[data-testid="place-order"]'
    loading = '[data-testid="loading"]'


class OrderCompleteLocators:

    container = '[data-testid="order-complete"]'
    order_no = '[data-testid="complete-order-no"]'
    total = '[data-testid="complete-total"]'
    complete_item = '[data-testid="complete-item"]'
