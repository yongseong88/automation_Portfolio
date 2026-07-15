"""장바구니 페이지 로케이터."""


class CartLocators:

    def item_remove(self, product_id: int):
        remove_loc = f'[data-testid="item-remove"][data-id="{product_id}"]'
        return remove_loc

    def item_plus(self, product_id: int):
        plus_loc = f'[data-testid="item-plus"][data-id="{product_id}"]'
        return plus_loc

    def item_minus(self, product_id: int):
        minus_loc = f'[data-testid="item-minus"][data-id="{product_id}"]'
        return minus_loc

    def item_qty(self, product_id: int):
        item_qty_loc = f'[data-testid="cart-item"][data-id="{product_id}"] [data-testid="item-qty"]'
        return item_qty_loc

    empty = '[data-testid="cart-empty"]'
    cart_body = '[data-testid="cart-body"]'
    summary = '[data-testid="summary"]'
    subtotal = '[data-testid="subtotal"]'
    shipping = '[data-testid="shipping"]'
    ship_note = '[data-testid="ship-note"]'
    total = '[data-testid="total"]'
    checkout = '[data-testid="checkout"]'

    item = '[data-testid="cart-item"]'
    item_name = '[data-testid="item-name"]'
    # item_qty = '[data-testid="item-qty"]'
    # item_plus = '[data-testid="item-plus"]'
    # item_minus = '[data-testid="item-minus"]'



    # item_remove = '[data-testid="item-remove"]'
    item_line = '[data-testid="item-line"]'
