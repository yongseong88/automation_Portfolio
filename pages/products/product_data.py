import random
from pages.commons.common_data import Commondata

class Productdata():
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.common_data = Commondata(base_url)


    def get_random_qty(self, qty, max_limit=10):
        """담을 수량을 랜덤으로 반환 (재고 이내, 기본 최대 5개)."""
        if qty <= 1:
            return 1
        upper = min(qty, max_limit)  # 재고와 상한 중 작은 값
        return random.randint(1, upper)