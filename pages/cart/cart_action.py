from pages import BasePage, CartPage
from playwright.sync_api import Page
from pages.cart.cart_data import Cartdata

import random


class Cartaction(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.cart_data = Cartdata(self.page, base_url)
        self.cart_page = CartPage(self.page, base_url)


    def remove_random_items(self):
        """장바구니에서 랜덤한 개수의 상품을 골라 제거 (뼈대)."""
        cart_items = self.cart_data.get_cart_items()

        if not cart_items:  # 빈 장바구니 방어
            return True

        random.shuffle(cart_items)  # 먼저 섞고
        random_cnt = random.randint(1, len(cart_items))  # 1~전체 개
        target_items = cart_items[:random_cnt]  # 앞에서 n개
        remove_result = []
        print(f"target_items 길이: {len(target_items)}")

        for target_item in target_items:
            product_code = target_item['cart_in_product_code']
            self.cart_page.item_remove(product_code)

            cart_response = self.cart_data.get_cart_response()
            cart_items_after = self.cart_data.get_cart_items()

            still_exists = any(
                ci.get("cart_in_product_code") == product_code for ci in cart_items_after
            )

            is_pass = cart_response.status == 200 and not still_exists
            remove_result.append("Pass" if is_pass else "Fail")

        success = sum(1 for r in remove_result if r == "Pass")
        return success == len(remove_result)


    def items_random_update(self):
        """장바구니 상품의 수량을 랜덤 변경하고, API 응답으로 검증."""
        cart_items = self.cart_data.get_cart_items()

        if not cart_items:
            return False

        random.shuffle(cart_items)
        random_cnt = random.randint(1, len(cart_items))
        target_items = cart_items[:random_cnt]

        update_result = []

        for target_item in target_items:
            product_code = target_item.get('cart_in_product_code', 0)
            product_qty = target_item.get('cart_in_product_qty', 0)
            product_stock = target_item.get('cart_in_product_stock', 0)

            target_qty = random.randint(1, product_stock)  # 목표 수량 (1 ~ 재고)
            diff = abs(target_qty - product_qty)  # 클릭 횟수

            if target_qty == product_qty:
                continue  # 변경 없음

            if target_qty > product_qty:
                self.cart_page.increase_qty(product_code, diff)  # + 로 증가
            else:
                self.cart_page.decrease_qty(product_code, diff)  # - 로 감소

            # ★ API 응답으로 검증 (UI 반환값이 아니라)
            api_qty = self.cart_data.get_qty_from_api(product_code)
            update_result.append("Pass" if api_qty == target_qty else "Fail")

        if not update_result:  # 변경할 게 없었으면 실패 아님
            return True

        success = sum(1 for r in update_result if r == "Pass")
        return success == len(update_result)






        #     if current_qty:
        #         update_status.append({
        #             "update_qty_product": product_code,
        #             "update_qty": current_qty
        #         })
        #
        # update_cart_items = self.cart_data.get_cart_items()
        #
        #
        #
        # for uc in update_status:
        #     update_product_code = us.get("update_qty_product", 0)
        #     update_product_qty = us.get("update_qty", 0)
        #
        #     for us in update_cart_items:
        #         current_product_code = uc.get("cart_in_product_code", 0)
        #         current_product_qty = uc.get("cart_in_product_qty", 0)
        #
        #         if current_product_code == update_product_code and current_product_qty ==  update_product_qty:
        #             update_result.append("pass")
        #
        # update_success_count = sum(1 for result in update_result if result == "pass")
        #
        # if update_success_count == len(update_status):
        #     return True
        #
        # else:
        #     return False

        # return target_items

    # def decrease_random_items(self):
    #     """장바구니에서 랜덤한 개수의 상품을 골라 제거 (뼈대)."""
    #     cart_items = self.cart_data.get_cart_items()
    #
    #     if not cart_items:  # 빈 장바구니 방어
    #         return
    #
    #     random.shuffle(cart_items)  # 먼저 섞고
    #     random_cnt = random.randint(1, len(cart_items))  # 1~전체 개
    #     target_items = cart_items[:random_cnt]  # 앞에서 n개
    #
    #     return target_items