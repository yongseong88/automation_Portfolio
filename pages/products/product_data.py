import random
from pages.commons.common_data import Commondata

class Productdata():

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.common_data = Commondata(base_url)


    def get_random_qty(self, qty, max_limit=5):
        """담을 수량을 랜덤으로 반환 (재고 이내, 기본 최대 5개)."""
        if qty <= 1:
            return 1

        upper = min(qty, max_limit)  # 재고와 상한 중 작은 값
        return random.randint(1, upper)

    def get_route_plan(self, target_cnt):
        """
            경로 3종이 최소 1회씩 포함된 실행 계획(경로 리스트)을 만든다.
            경로별로 random.choice 를 매번 뽑으면 특정 경로가 한 번도 안 걸릴 수 있어
            3종을 먼저 깔고, 남는 횟수만 랜덤으로 채운 뒤 순서를 섞는다.
            target_cnt 가 3보다 작으면 3회로 올린다 (경로 커버리지 우선).
        """
        route_list = ["category", "home_deal", "home_all"]

        if target_cnt >= len(route_list):
            plan = list(route_list)  # 3종 보장
            plan += random.choices(route_list, k=target_cnt - len(plan))  # 나머지 랜덤(중복 허용)

        else:
            plan = random.sample(route_list, k=target_cnt)  # 3종 중 일부(중복 없이)

        random.shuffle(plan)
        return plan



