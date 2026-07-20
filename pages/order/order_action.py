from pages import BasePage, OrderPage
from playwright.sync_api import Page
from pages.commons.common_action import Commonaction
from pages.commons.common_data import Commondata
from locators import OrderLocators, OrderCompleteLocators, BaseLocators
from pages.order.order_data import Orderdata
from utilities.File_read import Filereadutil


class Orderaction(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.order_page = OrderPage(self.page, base_url)
        self.order_data = Orderdata(base_url)
        self.common_data = Commondata(base_url)
        self.common_action = Commonaction(self.page, base_url)

        self.ol = OrderLocators()
        self.ocl = OrderCompleteLocators()
        self.bl = BaseLocators()

        read_util = Filereadutil()

    # --- 주문자 정보 입력 ---
    def fill_orderer(self):
        """주문자 정보(이름/연락처/이메일) 입력."""
        buyer_info = self.order_data.buyer_Information()
        name = buyer_info['name']
        phone = buyer_info['phone']
        email_address = buyer_info['email']


        self.order_page.name(name)
        self.order_page.phone(phone)
        self.order_page.email(email_address)

    # --- 배송지 정보 입력 ---
    def fill_delivery(self, request: str = ""):
        """배송지 정보(받는 사람/연락처/주소/요청사항) 입력."""
        delivery_info = self.order_data.delivery_Information()

        recipient = delivery_info['recipient']
        phone = delivery_info['delivery_phone']
        address = delivery_info['address']

        self.order_page.recipient(recipient)
        self.order_page.recive_phone(phone)
        self.order_page.address(address)

        if request:
            self.order_page.delivery_request(request)





