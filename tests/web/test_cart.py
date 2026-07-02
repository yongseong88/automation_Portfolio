"""장바구니 페이지 UI 테스트 (POM 사용).

패턴: API(CartApi)로 상태를 arrange 하고, UI(CartPage)로 assert.
"""

from playwright.sync_api import Page, expect

from pages import CartApi, CartPage

SPINACH_ID = 1  # 시금치 3,900원
HANWOO_ID = 7  # 한우 39,900원


def test_empty_cart_state(page: Page, base_url: str):
    cart = CartPage(page, base_url).open()
    expect(cart.empty).to_be_visible()


def test_cart_total_with_shipping_fee(api, page: Page, base_url: str):
    # arrange: 시금치 3,900 x 5 = 19,500 → 4만 미만 → 배송비 3,000
    CartApi(api).add(SPINACH_ID, qty=5)
    cart = CartPage(page, base_url).open()
    expect(cart.subtotal).to_have_text("19,500원")
    expect(cart.shipping).to_have_text("3,000원")
    expect(cart.total).to_have_text("22,500원")


def test_cart_free_shipping_over_threshold(api, page: Page, base_url: str):
    # 한우 39,900 x 2 = 79,800 → 무료배송
    CartApi(api).add(HANWOO_ID, qty=2)
    cart = CartPage(page, base_url).open()
    expect(cart.shipping).to_have_text("무료")


def test_cart_remove_item(api, page: Page, base_url: str):
    CartApi(api).add(SPINACH_ID, qty=1)
    cart = CartPage(page, base_url).open()
    expect(cart.items).to_have_count(1)
    cart.remove_first()
    expect(cart.empty).to_be_visible()
