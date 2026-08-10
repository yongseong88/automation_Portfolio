import re

from pages import BasePage, OrderPage
from playwright.sync_api import Page
from pages.commons.common_action import Commonaction
from pages.commons.common_data import Commondata
from locators import OrderLocators, OrderCompleteLocators, BaseLocators
from pages.order.order_data import Orderdata
from utilities.File_read import Filereadutil
from utilities.logger import get_logger

logger = get_logger(__name__)


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

        self.File_read_util = Filereadutil()

    # --- 주문자 정보 입력 ---
    def fill_orderer(self):
        """주문자 정보(이름/연락처/이메일) 입력."""
        buyer_info = self.order_data.buyer_Information()
        name = buyer_info['name']
        phone = buyer_info['phone']
        email_address = buyer_info['email']

        self.order_page.input_name(name)
        self.order_page.input_phone(phone)
        self.order_page.input_email(email_address)

    # --- 배송지 정보 입력 ---
    def fill_delivery(self, request: str = ""):
        """배송지 정보(받는 사람/연락처/주소/요청사항) 입력."""
        delivery_info = self.order_data.delivery_Information()

        recipient = delivery_info['recipient']
        phone = delivery_info['delivery_phone']
        address = delivery_info['address']

        self.order_page.input_recipient(recipient)
        self.order_page.input_recive_phone(phone)
        self.order_page.input_address(address)

        if request:
            self.order_page.input_delivery_request(request)

    def clear_field(self, field: str):
        """지정한 입력 필드를 비운다."""
        clear_field = getattr(self.ol, field)
        self.input_text(clear_field, "")
        # self.set_field(field, "")

    # def set_field(self, field: str, value: str):
    #     """지정한 입력 필드의 값을 새로 채운다(빈 문자열이면 비움)."""
    #     self.input_text(self.input_locator(field), value)



    def error_msg(self):
        ui_json_path = self.File_read_util.read_filepath("config/", "ui.json")
        ui_data = self.File_read_util.read_file(ui_json_path)

        order_invalid_msg = ui_data.get('order', {}).get('required_field', "")

        return {
            "invalid_order_msg" : order_invalid_msg
        }

    def order_valid_check(self, field) -> bool:
        try:
            msg = self.error_msg()
            error_field = getattr(self.ol, f"{field}_error")
            required_msg = msg.get("invalid_order_msg", "")

            assert self.check_url(re.compile(r"/order")), "주문 실패 후 주문서 페이지가 유지되지 않음"
            assert self.check_text(error_field, required_msg), f"필수 입력 에러 문구가 노출되지 않음: {required_msg}"

            return True

        except AssertionError:
            logger.exception("주문 실패 검증 불일치: field=%s, url=%s", field, self.page.url)
            return False

        except Exception:
            # 요소 조회/페이지 접근 자체가 실패한 경우는 검증 결과로 볼 수 없으므로 재던짐
            logger.exception("주문 실패 검증 중 오류: field=%s, url=%s", field, self.page.url)
            raise