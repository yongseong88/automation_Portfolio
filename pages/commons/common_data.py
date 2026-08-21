import random
from configparser import NoOptionError, NoSectionError

from utilities.File_read import Filereadutil
from utilities.logger import get_logger

logger = get_logger(__name__)


class Commondata():
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.File_read_util = Filereadutil()

    def get_product_info(self):
        """products.json 을 읽어 무작위 순서로 반환. 읽기 실패/형식 불일치면 None."""
        try:
            product_json_path = self.File_read_util.read_filepath("config", "products.json")
            product_data = self.File_read_util.read_file(product_json_path)

            if isinstance(product_data, list):
                random.shuffle(product_data)
                return product_data

            else:
                # 파일이 없거나(None) JSON 구조가 리스트가 아닌 경우 → 호출측에서 None 방어
                logger.warning("상품 데이터가 리스트가 아님 (type=%s) → None 반환", type(product_data).__name__)
                return None

        except Exception:
            # 경로 계산 실패, 권한 문제 등 예상 못 한 읽기 오류
            logger.exception("상품 데이터 파일 읽기 실패: config/products.json")
            raise


    def get_available_product(self):
        """재고 있는 상품 중 하나를 무작위로 반환. 후보가 없으면 None."""
        # 후보가 하나도 없으면 random.choice 가 IndexError → 호출측 계약대로 None 반환
        try:
            product_data = self.get_product_info()

            # 품절(stock == 0) 상품은 담기 불가 → 재고 있는 상품만 후보로
            # 데이터 없음(None) → TypeError, 원소가 dict 가 아님 → AttributeError
            try:
                available = [p for p in product_data if p.get("stock", 0) > 0]

            except TypeError:
                # 상품 데이터 자체가 없거나(None) stock 값이 숫자가 아님(예: "30")
                logger.warning("상품 데이터를 사용할 수 없음 → None 반환: data=%r", product_data)
                raise
                # return None

            except AttributeError:
                # 리스트 원소가 dict 가 아님 (products.json 구조 변경)
                logger.exception("상품 데이터 구조가 dict 리스트가 아님: data=%r", product_data[:3])
                raise

            target_product = random.choice(available)

            return {
                "product_id": target_product.get("id"),
                "product_name": target_product.get("name"),
                "product_category": target_product.get("category"),
                "product_stock": target_product.get("stock")
            }

        except IndexError:
            logger.warning("재고 있는 상품 없음 (전체 %d건 모두 품절) → None 반환", len(product_data))
            return None



    def get_product_price(self, product_id):
        """상품 id 로 단가를 조회. 없으면 0 (담기 예산 계산에서 제외됨)."""
        product_data = self.get_product_info()

        for product in product_data or []:
            if product.get("id") == product_id:
                return product.get("price", 0)

        logger.warning("상품 단가를 찾지 못함: product_id=%s", product_id)

        return 0

    def account_config(self):
        """테스트 계정 정보 반환 (CI 환경변수 → 없으면 config.ini)."""
        try:

            return {
                "valid_id": self.File_read_util.readConfig("Account", f"valid_id"),
                "valid_pwd": self.File_read_util.readConfig("Account", f"valid_pwd"),
                "invalid_id": self.File_read_util.readConfig("Account", "invalid_id"),
                "invalid_pwd": self.File_read_util.readConfig("Account", "invalid_pwd")
            }

        except (NoSectionError, NoOptionError):
            # config.ini 에 [Account] 섹션/키가 없음 (CI 라면 환경변수 미설정)
            logger.exception("계정 설정 누락: config.ini 의 [Account] 섹션/키 또는 ACCOUNT_* 환경변수를 확인하세요")
            raise

        except Exception:
            # config.ini 자체가 없거나 파싱 실패 → 계정 없이 로그인 테스트 불가하므로 재던짐
            logger.exception("계정 설정 읽기 실패")
            raise
