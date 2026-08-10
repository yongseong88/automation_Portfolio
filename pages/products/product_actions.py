import random
import math
from locators import BaseLocators, CategoryLocators
from pages import BasePage, HomePage, ProductPage, CategoryPage
from playwright.sync_api import Page
from pages.cart.cart_data import Cartdata
from pages.commons.common_action import Commonaction
from pages.commons.common_data import Commondata
from pages.products.product_data import Productdata
from utilities.logger import get_logger


logger = get_logger(__name__)


class Productaction(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.common_data = Commondata(base_url)
        self.product_data = Productdata(base_url)
        self.cart_data = Cartdata(self.page, base_url)

        self.home_page = HomePage(self.page, base_url)
        self.category_page = CategoryPage(self.page, base_url)
        self.product_page = ProductPage(self.page, base_url)

        self.common_action = Commonaction(self.page, base_url)

        self.bl = BaseLocators()
        self.cl = CategoryLocators()

        self.product_info = self.common_data.get_available_product()

    def random_product_selected(self):
        """홈(특가/전체) / 카테고리 경로를 랜덤으로 섞어 여러 상품을 장바구니에 담고 검증."""

        target_cnt = random.randint(1, 5)  # 1~5개 담기

        # 경로 3종(home_deal/home_all/category)이 최소 1회씩 실행되도록 계획을 먼저 만든다
        route_plan = self.product_data.get_route_plan(target_cnt)
        # target_cnt = len(route_plan)  # 3종 보장을 위해 늘어났을 수 있음
        add_result = []

        for route in route_plan:
            if route == "home_deal":
                product = self.home_page.deal_product_selected()  # 홈 특가 → 상세

            elif route == "home_all":
                product = self.home_page.all_product_selected()  # 홈 전체 → 상세

            else:
                product = self.category_page.category_product_selected()  # 카테고리 진입 → 상세
                # product = self.common_action.all_product_selected(click_product_category)  # → 상세

            # --- 여기는 모두 '상품 상세 페이지' ---
            product_code = product.get("target_product_code", 0)
            product_stock = product.get("target_product_stock", 0)

            before_qty = self.cart_data.get_qty_from_api(product_code)  # 담기 전 수량

            remaining = product_stock - before_qty

            if remaining <= 0:
                self.common_action.logo_selected()
                continue

            target_qty = self.product_data.get_random_qty(remaining) # 담을 수량

            self.product_page.increase_qty(target_qty - 1)  # 수량 조절 (기본 1개라 -1)
            self.product_page.add_to_cart()  # 담기
            self.product_page.add_success_toast()  # 토스트 확인

            expected_qty = before_qty + target_qty  # 누적 수량 값

            # --- 장바구니 API 로 검증 ---
            cart_response = self.cart_data.get_cart_response()
            cart_items = self.cart_data.get_cart_items()

            target = next(
                (ci for ci in cart_items if ci.get("cart_in_product_code") == product_code),
                None,
            )

            is_pass = (
                    cart_response.status == 200
                    and target is not None
                    and target.get("cart_in_product_qty") == expected_qty
            )

            actual_qty = target.get("cart_in_product_qty") if target else None

            log = logger.info if is_pass else logger.warning  # 성공/실패 레벨 구분
            log(
                "[%s] 경로=%s 상품=%s 이전=%s 담기=%s 기대=%s 실제=%s status=%s",
                "Pass" if is_pass else "Fail",
                route, product_code, before_qty, target_qty, expected_qty,
                actual_qty, cart_response.status
            )


            add_result.append("Pass" if is_pass else "Fail")

            self.common_action.logo_selected()  # 홈 복귀 (다음 반복 준비)

        if not add_result:
            return True

        success = sum(1 for r in add_result if r == "Pass")
        fail = len(add_result) - success
        logger.info(
            "=== 결과: 총 %s건 (목표 %s건) / 성공 %s / 실패 %s ===",
            len(add_result), target_cnt, success, fail
        )
        return success == len(add_result)  # 실제 시도한 것들이 전부 통과하면 True

    def product_detail_add_to_cart(self, product_code, product_stock, target_qty=None):
        """상품 상세에서 담기 버튼 클릭 후 담은 상품 id 와 수량 반환.

        target_qty 를 주면 그 수량 그대로 담는다 (금액 조건을 맞춰야 하는 시나리오용).
        생략하면 재고 안에서 랜덤으로 뽑는다 (기존 동작).
        """

        if target_qty is None:
            target_qty = self.product_data.get_random_qty(product_stock)

        print(f"상품 코드: {product_code}")
        print(f"상품 수량: {target_qty}")

        self.product_page.increase_qty(target_qty - 1)  # 스테퍼는 1에서 시작 → 최종 수량 = target_qty
        self.product_page.add_to_cart()
        self.product_page.add_success_toast()

        return product_code, target_qty

    def shipping_verification(self):
        """
            합계가 무료배송 기준 '미만'인 장바구니를 만들고 API 배송비를 반환.
            카트는 전역이라 앞선 테스트 잔여물이 남아 있으면 합계가 기준을 넘어버린다.
            → 빈 카트에서 시작하고, 담기 '전에' 예상 합계를 계산해 기준을 넘지 않는 수량만 담는다.
            또한 남은 예산을 '남은 상품 수'로 나눠 배분해, 앞 상품이 예산을 독식하지 않게 한다.
        """
        threshold = self.cart_data.get_free_shipping_threshold()  # 무료배송 기준 금액
        target_cnt = random.randint(1, 3)  # 담을 상품 종류 수

        # 경로 3종(home_deal/home_all/category)이 최소 1회씩 실행되도록 계획을 먼저 만든다
        route_plan = self.product_data.get_route_plan(target_cnt)
        plan_len = len(route_plan)  # 실제 시도 횟수 (target_cnt 대신 계획 길이 사용)
        added_codes = []

        for idx, route in enumerate(route_plan):
            if route == "home_deal":
                product = self.home_page.deal_product_selected()  # 홈 특가 → 상세
            elif route == "home_all":
                product = self.home_page.all_product_selected()  # 홈 전체 → 상세
            else:
                product = self.category_page.category_product_selected()  # 카테고리 → 상세

            product_code = product.get("target_product_code", 0)
            product_stock = product.get("target_product_stock", 0)

            # 담기 전에 남은 예산으로 몇 개까지 담을 수 있는지 계산한다
            subtotal = self.cart_data.get_subtotal()  # 배송비 뺀 상품 합계
            price = self.common_data.get_product_price(product_code)  # 상품 id 로 단가 조회

            total_budget = threshold - 1 - subtotal  # 기준 '미만' 이어야 하므로 -1
            remaining_slots = plan_len - idx  # 이번 포함 남은 상품 수
            my_budget = total_budget // remaining_slots  # 이번 상품에 배분된 예산

            # 마지막 상품은 남은 예산을 모두 사용 (배분 나머지를 버리지 않도록)
            if remaining_slots == 1:
                my_budget = total_budget

            if price <= 0 or my_budget < price:
                # 배분 예산으로는 한 개도 못 담는 상품 → 건너뛴다
                logger.info(
                    "[Skip] 예산 부족: 상품=%s 단가=%s 현재합계=%s 전체예산=%s 배분예산=%s",
                    product_code, price, subtotal, total_budget, my_budget
                )
                self.common_action.logo_selected()
                continue

            affordable_qty = min(product_stock, my_budget // price)

            if affordable_qty <= 0:
                logger.info(
                    "[Skip] 담을 수량 없음: 상품=%s 재고=%s 배분예산=%s",
                    product_code, product_stock, my_budget
                )
                self.common_action.logo_selected()
                continue

            self.product_detail_add_to_cart(product_code, affordable_qty)
            added_codes.append(product_code)

            logger.info(
                "[Add] 상품=%s 단가=%s 수량=%s (재고=%s 배분예산=%s 남은슬롯=%s)",
                product_code, price, affordable_qty, product_stock, my_budget, remaining_slots
            )

            self.common_action.logo_selected()  # 홈 복귀 (다음 반복 준비)

        subtotal = self.cart_data.get_subtotal()
        shipping = self.cart_data.get_shipping()
        logger.info(
            "배송비 시나리오 준비 완료: 담은종류=%s(%s) 합계=%s (기준=%s 미만) 배송비=%s",
            len(set(added_codes)), added_codes, subtotal, threshold, shipping
        )

        return shipping


    def shipping_free(self):
        """
            합계가 무료배송 기준 '이상'인 장바구니를 만들고 API 배송비를 반환.
            빈 카트에서 시작해, 기준까지 부족한 금액을 계획된 상품 수로 나눠 나누어 담는다.
            (첫 상품이 부족액을 다 채워버리면 항상 1종류만 담기게 되므로 분담시킨다)
            마지막 상품이 남은 부족액을 전부 채워 기준을 확실히 넘기고,
            재고 부족으로 못 채우면 경로를 더 뽑아 이어 담는다.
        """
        self.cart_data.clear_cart()  # 잔여물 제거 (조건을 결정적으로 만들기 위함)

        threshold = self.cart_data.get_free_shipping_threshold()  # 무료배송 기준 금액
        target_cnt = random.randint(1, 5)  # 담을 상품 종류 수

        # 경로 3종(home_deal/home_all/category)이 최소 1회씩 실행되도록 계획을 먼저 만든다
        route_plan = self.product_data.get_route_plan(target_cnt)
        added_codes = []

        # 기준을 채우기 전에 계획이 끝나면 경로를 더 뽑아 이어 담는다
        plan_len = len(route_plan)
        max_attempts = plan_len + 10
        attempt = 0

        while attempt < max_attempts:
            subtotal = self.cart_data.get_subtotal()  # 배송비 뺀 상품 합계

            if subtotal >= threshold:
                break  # 기준 도달 → 더 담을 필요 없음

            if attempt < plan_len:
                route = route_plan[attempt]
                remaining_slots = plan_len - attempt  # 이번 포함 계획상 남은 상품 수

            else:
                # 계획을 다 쓰고도 미달 → 보충 단계. 남은 부족액을 한 번에 채운다
                route = random.choice(route_plan)
                remaining_slots = 1

            attempt += 1

            if route == "home_deal":
                product = self.home_page.deal_product_selected()  # 홈 특가 → 상세
            elif route == "home_all":
                product = self.home_page.all_product_selected()  # 홈 전체 → 상세
            else:
                product = self.category_page.category_product_selected()  # 카테고리 → 상세

            product_code = product.get("target_product_code", 0)
            product_stock = product.get("target_product_stock", 0)

            price = self.common_data.get_product_price(product_code)  # 상품 id 로 단가 조회

            if price <= 0 or product_stock <= 0:
                logger.info(
                    "[Skip] 담을 수 없음: 상품=%s 단가=%s 재고=%s",
                    product_code, price, product_stock
                )
                self.common_action.logo_selected()
                continue

            # 부족액을 남은 상품 수로 나눠 분담 (마지막 상품이 나머지를 전부 채움)
            shortage = threshold - subtotal
            share = shortage if remaining_slots == 1 else math.ceil(shortage / remaining_slots)
            need_qty = max(1, math.ceil(share / price))  # 계획된 상품은 최소 1개는 담는다

            # 이미 담긴 수량만큼 재고가 줄어 있으므로 남은 재고 안에서만 담는다
            before_qty = self.cart_data.get_qty_from_api(product_code)
            remaining_stock = product_stock - before_qty
            add_qty = min(need_qty, remaining_stock)

            if add_qty <= 0:
                logger.info(
                    "[Skip] 재고 소진: 상품=%s 재고=%s 담긴수량=%s",
                    product_code, product_stock, before_qty
                )
                self.common_action.logo_selected()
                continue

            # 계산한 수량을 그대로 담아야 하므로 target_qty 로 명시 (랜덤 재추첨 방지)
            self.product_detail_add_to_cart(product_code, product_stock, target_qty=add_qty)
            added_codes.append(product_code)

            logger.info(
                "[Add] 상품=%s 단가=%s 수량=%s (부족액=%s 분담액=%s 필요수량=%s 남은재고=%s 남은슬롯=%s)",
                product_code, price, add_qty, shortage, share, need_qty, remaining_stock, remaining_slots
            )

            self.common_action.logo_selected()  # 홈 복귀 (다음 반복 준비)

        subtotal = self.cart_data.get_subtotal()
        shipping = self.cart_data.get_shipping()

        logger.info(
            "무료배송 시나리오 준비 완료: 담은종류=%s(%s) 합계=%s (기준=%s 이상) 배송비=%s",
            len(set(added_codes)), added_codes, subtotal, threshold, shipping
        )

        return shipping
