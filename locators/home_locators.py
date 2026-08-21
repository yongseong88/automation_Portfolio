"""홈 페이지 로케이터.

홈은 두 영역으로 나뉜다.
- 구좌(캐러셀): /api/sections 의 key(deal/popular/new/limited/budget) 별 섹션.
  상품을 5개씩 끊어 보여주고 좌우 화살표로 다음 묶음을 노출한다.
- 전체 상품 그리드: 페이지네이션 없이 앞쪽 일부만 렌더된다.
"""


class HomeLocators():

    # --- 구좌(캐러셀) ---
    def section(self, key: str):
        return f'[data-testid="section-{key}"]'

    def section_grid(self, key: str):
        return f'[data-testid="section-grid-{key}"]'

    def section_card(self, key: str, product_id: int):
        """구좌 안의 특정 상품 카드. 현재 묶음에 없으면 매칭되지 않는다."""
        return f'[data-testid="section-grid-{key}"] [data-id="{product_id}"]'

    def section_cards(self, key: str):
        """구좌에 현재 노출된 상품 카드 전체."""
        return f'[data-testid="section-grid-{key}"] [data-testid="product-card"]'

    def section_prev(self, key: str):
        return f'[data-testid="section-prev-{key}"]'

    def section_next(self, key: str):
        return f'[data-testid="section-next-{key}"]'

    def section_page(self, key: str):
        """'{현재} / {전체}' 형태의 구좌 페이지 표시."""
        return f'[data-testid="section-page-{key}"]'

    # --- 전체 상품 그리드 ---
    def all_grid(self, product_id: int):
        return f'[data-testid="product-grid"] [data-id="{product_id}"]'

    sections = '[data-testid="sections"]'
    product_grid = '[data-testid="product-grid"]'
    product_cards = '[data-testid="product-grid"] [data-testid="product-card"]'
    search_title = '[data-testid="search-title"]'
    empty = '[data-testid="empty"]'
