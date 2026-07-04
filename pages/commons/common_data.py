import random
from utilities.File_read import Filereadutil


class Commondata():
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.File_read_util = Filereadutil()

    def get_product_info(self):
        product_json_path = self.File_read_util.read_filepath("config/", "products.json")
        product_data = self.File_read_util.read_file(product_json_path)

        if isinstance(product_data, list):
            random.shuffle(product_data)
            return product_data

        else:
            return None

    def get_deal_product(self):
        product_data = self.get_product_info()

        # 특가 상품만 모으기
        deal_products = [p for p in product_data if p.get("badge") == "특가"]

        if not deal_products:  # 특가가 없을 때 방어
            return None

        return random.choice(deal_products)["id"]  # 그중 랜덤 하나

    def get_all_product(self):
        product_data = self.get_product_info()

        if not product_data:  # 빈 리스트 방어
            return None

        target_product = random.choice(product_data)

        target_id = target_product.get("id")
        target_name = target_product.get("name")

        return {
            "product_id": target_id,
            "product_name": target_name
        }

        # return random.choice(product_data)["id"]





