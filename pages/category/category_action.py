"""카테고리 API 응답 검증 액션."""

from pages import BasePage, CategoryPage
from playwright.sync_api import Page
from utilities.logger import get_logger

logger = get_logger(__name__)


class Categoryaction(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.category_page = CategoryPage(self.page, base_url)

    def get_items(self, response) -> list:
        """
            응답 바디에서 상품 목록(items)을 꺼낸다.
            items 키가 없으면 AssertionError → 호출한 검증 함수가 False 를 돌려준다.
        """
        body = response.json()
        assert "items" in body, "응답 바디에 items 키가 없음"

        return body["items"]

    def category_valid_check(self, response, target_category) -> bool:
        """응답의 모든 상품이 선택한 카테고리인지 검증."""
        try:
            items = self.get_items(response)
            # 어떤 카테고리가 섞였는지 알아야 원인 파악이 되므로 실제 값도 메시지에 남긴다
            assert all(item["category"] == target_category for item in items), \
                f"선택한 카테고리와 다른 상품이 응답에 포함됨: 기대={target_category}, 실제={sorted({item['category'] for item in items})}"

        except AssertionError:
            logger.exception("카테고리 응답 검증 실패: category=%s", target_category)
            return False

        except Exception:
            # 응답 파싱 실패, 키 구조 변경 등은 검증 결과로 볼 수 없으므로 재던짐
            logger.exception("카테고리 응답 검증 중 오류: category=%s", target_category)
            raise

        logger.info("카테고리 응답 검증 완료: category=%s, count=%s", target_category, len(items))

        return True

    def sort_valid_check(self, response, field: str, reverse: bool = False) -> bool:
        """응답의 특정 필드가 정렬 상태인지 검증. reverse=True 면 내림차순."""
        order = "내림차순" if reverse else "오름차순"

        try:
            values = [item[field] for item in self.get_items(response)]
            assert values == sorted(values, reverse=reverse), \
                f"{field}이(가) {order}으로 정렬되지 않음: {values}"

        except AssertionError:
            logger.exception("정렬 검증 실패: field=%s, order=%s", field, order)
            return False

        except Exception:
            logger.exception("정렬 검증 중 오류: field=%s, order=%s", field, order)
            raise

        logger.info("정렬 검증 완료: field=%s, order=%s, count=%s", field, order, len(values))

        return True

    def id_asc_check(self, response) -> bool:
        """기본순: id 오름차순 검증."""
        return self.sort_valid_check(response, "id")

    def price_asc_check(self, response) -> bool:
        """낮은 가격순: price 오름차순 검증."""
        return self.sort_valid_check(response, "price")

    def price_desc_check(self, response) -> bool:
        """높은 가격순: price 내림차순 검증."""
        return self.sort_valid_check(response, "price", reverse=True)

    def name_asc_check(self, response) -> bool:
        """이름순: name 오름차순 검증."""
        return self.sort_valid_check(response, "name")
