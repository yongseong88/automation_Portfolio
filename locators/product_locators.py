"""상품 상세 페이지 로케이터."""


class ProductLocators:
    DETAIL = "detail"
    NAME = "detail-name"
    PRICE = "detail-price"
    NOT_FOUND = "not-found"
    # 수량 스테퍼
    QTY = "qty"
    QTY_PLUS = "qty-plus"
    QTY_MINUS = "qty-minus"
    # 담기 / 품절 / 토스트
    ADD_TO_CART = "add-to-cart"
    SOLD_OUT_BTN = "sold-out-btn"
    TOAST_OK = "toast-ok"
