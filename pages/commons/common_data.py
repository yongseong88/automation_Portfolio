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

    def get_available_product(self):
        product_data = self.get_product_info()

        if not product_data:  # 빈 리스트 방어
            return None

        # 품절(stock == 0) 상품은 담기 불가 → 재고 있는 상품만 후보로
        available = [p for p in product_data if p.get("stock", 0) > 0]

        if not available:
            return None

        target_product = random.choice(available)

        return {
            "product_id": target_product.get("id"),
            "product_name": target_product.get("name"),
            "product_category": target_product.get("category"),
            "product_stock": target_product.get("stock")
        }

    def account_config(self):

        try:

            return {
                "valid_id": self.File_read_util.readConfig("Account", f"valid_id"),
                "valid_pwd": self.File_read_util.readConfig("Account", f"valid_pwd"),
                "invalid_id": self.File_read_util.readConfig("Account", "invalid_id"),
                "invalid_pwd": self.File_read_util.readConfig("Account", "invalid_pwd")

            }

        except AssertionError as e:
            print(f"AssertionError: {e}")




    # def get_all_product(self):
    #     product_data = self.get_product_info()
    #
    #     if not product_data:  # 빈 리스트 방어
    #         return None
    #
    #     target_product = random.choice(product_data)
    #
    #     target_id = target_product.get("id")
    #     target_name = target_product.get("name")
    #     target_category = target_product.get("category")
    #
    #     return {
    #         "product_id": target_id,
    #         "product_name": target_name,
    #         "product_category": target_category
    #     }
