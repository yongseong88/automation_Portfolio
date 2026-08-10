from pages import BasePage, CartPage
from playwright.sync_api import Page
from pages.cart.cart_data import Cartdata
import random
from utilities.logger import get_logger

logger = get_logger(__name__)


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

        logger.info("제거 대상: %s건 (장바구니 총 %s건)", len(target_items), len(cart_items))

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

            log = logger.info if is_pass else logger.warning
            log(
                "[%s] 제거 상품=%s 잔존=%s 남은건수=%s status=%s",
                "Pass" if is_pass else "Fail",
                product_code, still_exists,
                len(cart_items_after), cart_response.status
            )

        success = sum(1 for r in remove_result if r == "Pass")
        fail = len(remove_result) - success
        logger.info(
            "=== 제거 결과: 총 %s건 / 성공 %s / 실패 %s ===",
            len(remove_result), success, fail
        )
        return success == len(remove_result)

    def items_random_update(self):
        """장바구니 상품의 수량을 랜덤 변경하고, API 응답으로 검증."""
        cart_items = self.cart_data.get_cart_items()

        if not cart_items:
            logger.info("장바구니가 비어 있어 수량 변경을 건너뜀")
            return False

        random.shuffle(cart_items)
        random_cnt = random.randint(1, len(cart_items))
        target_items = cart_items[:random_cnt]

        update_result = []
        logger.info("수량 변경 대상: %s건 (장바구니 총 %s건)", len(target_items), len(cart_items))

        for target_item in target_items:
            product_code = target_item.get('cart_in_product_code', 0)
            product_qty = target_item.get('cart_in_product_qty', 0)
            product_stock = target_item.get('cart_in_product_stock', 0)

            target_qty = random.randint(1, product_stock)  # 목표 수량 (1 ~ 재고)
            diff = abs(target_qty - product_qty)  # 클릭 횟수

            if target_qty == product_qty:
                logger.info(
                    "[Skip] 상품=%s 현재수량=%s 목표수량=%s (동일 → 변경 없음)",
                    product_code, product_qty, target_qty
                )
                continue

            if target_qty > product_qty:
                qty_action = self.cart_page.increase_qty  # + 로 증가
                direction = "증가"
            else:
                qty_action = self.cart_page.decrease_qty  # - 로 감소
                direction = "감소"

            for _ in range(diff):
                qty_action(product_code)

            # ★ API 응답으로 검증 (UI 반환값이 아니라)
            api_qty = self.cart_data.get_qty_from_api(product_code)
            is_pass = api_qty == target_qty
            update_result.append("Pass" if is_pass else "Fail")

            log = logger.info if is_pass else logger.warning
            log(
                "[%s] 상품=%s %s %s회 (재고=%s) 이전=%s 목표=%s 실제=%s",
                "Pass" if is_pass else "Fail",
                product_code, direction, diff, product_stock,
                product_qty, target_qty, api_qty
            )

        if not update_result:  # 변경할 게 없었으면 실패 아님
            logger.info("수량 변경 대상 없음 (전부 현재 수량과 동일)")
            return True

        success = sum(1 for r in update_result if r == "Pass")
        fail = len(update_result) - success
        logger.info(
            "=== 수량 변경 결과: 총 %s건 / 성공 %s / 실패 %s ===",
            len(update_result), success, fail
        )
        return success == len(update_result)



