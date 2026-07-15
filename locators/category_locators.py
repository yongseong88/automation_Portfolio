"""카테고리 페이지 로케이터."""


class CategoryLocators:
    def category(self, text):
        category_keyword = f'[data-testid="cat-{text}"]'
        return category_keyword

    sort_dropdown = '[data-testid="sort"]'
    default_sort = "id:asc"
    price_asc = "price:asc"
    price_desc = "price:desc"
    name_asc = "name:asc"





    # sort_dropdown = "sort"
    TITLE = "category-title"
    PRODUCT_CARD = "product-card"
    PRICE = "price"