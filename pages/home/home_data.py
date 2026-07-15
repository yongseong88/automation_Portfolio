import random

from pages.commons.common_data import Commondata
from utilities.File_read import Filereadutil


class Homedata():
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.common_data = Commondata(base_url)

    def get_deal_product(self):
        product_data = self.common_data.get_product_info()

        # 특가 상품만 모으기
        deal_products = [p for p in product_data if p.get("badge") == "특가" and p.get("stock", 0) > 0]

        if not deal_products:  # 특가가 없을 때 방어
            return None

        target_product = random.choice(deal_products)

        return {
            "product_id": target_product.get("id"),
            "product_stock": target_product.get("stock")
        }

        # return random.choice(deal_products)["id"]  # 그중 랜덤 하나





