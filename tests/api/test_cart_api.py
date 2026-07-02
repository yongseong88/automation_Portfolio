"""장바구니 API 테스트 (음성/양성 케이스).

순수 API 자동화 — UI 없이 CartApi 서비스 래퍼로 검증.
"""

from pages import CartApi

SPINACH_ID = 1  # 3,900원
TANGERINE_ID = 4  # 9,900원
SOLD_OUT_ID = 13  # 크루아상 = 품절
UNKNOWN_ID = 99999


def test_api_add_unknown_product_404(api):
    res = CartApi(api).add(UNKNOWN_ID, qty=1)
    assert res.status == 404


def test_api_add_sold_out_409(api):
    res = CartApi(api).add(SOLD_OUT_ID, qty=1)
    assert res.status == 409


def test_api_add_invalid_qty_422(api):
    res = CartApi(api).add(SPINACH_ID, qty=0)
    assert res.status == 422


def test_api_cart_subtotal_matches(api):
    cart_api = CartApi(api)
    cart_api.add(SPINACH_ID, qty=2)  # 3900*2
    cart_api.add(TANGERINE_ID, qty=1)  # 9900
    summary = cart_api.summary()
    assert summary["subtotal"] == 3900 * 2 + 9900
    assert summary["count"] == 3
