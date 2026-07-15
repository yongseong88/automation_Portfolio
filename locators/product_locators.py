"""상품 상세 페이지 로케이터."""


class ProductLocators():


    # 수량 스테퍼
    qty_plus = '[data-testid="qty-plus"]'
    qty_minus = '[data-testid="qty-minus"]'

    # 담기 / 품절 / 토스트
    add_cart = '[data-testid="add-to-cart"]'
    soldout_btn = '[data-testid="toast-ok"]'
    add_cart_toast = '[data-testid="sold-out-btn"]'


    DETAIL = "detail"
    NAME = "detail-name"
    PRICE = "detail-price"
    NOT_FOUND = "not-found"



    # 수량 스테퍼
    # QTY = "qty"
    # QTY_PLUS = "qty-plus"
    # QTY_MINUS = "qty-minus"

    # # 담기 / 품절 / 토스트
    # ADD_TO_CART = "add-to-cart"
    # SOLD_OUT_BTN = "sold-out-btn"
    # TOAST_OK = "toast-ok"
