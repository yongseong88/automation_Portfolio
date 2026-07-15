"""홈 페이지 로케이터."""


class HomeLocators():


    def deal_grid(self, product_id: int):
        DEAL_CARD_BY_ID = f'[data-testid="deal-grid"] [data-id="{product_id}"]'
        return DEAL_CARD_BY_ID

    def all_grid(self, product_id: int):
        ALL_CARD_BY_ID = f'[data-testid="product-grid"] [data-id="{product_id}"]'
        return ALL_CARD_BY_ID


    PRODUCT_GRID = "product-grid"
    DEAL_GRID = "deal-grid"
    SEARCH_TITLE = "search-title"
    PRODUCT_CARD = "product-card"  # 그리드 내부 카드
