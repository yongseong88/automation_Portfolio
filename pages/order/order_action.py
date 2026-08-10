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
        self.order_data = Orderdata(self.page, base_url)
        self.common_data = Commondata(base_url)
        self.common_action = Commonaction(self.page, base_url)

        self.ol = OrderLocators()
        self.ocl = OrderCompleteLocators()
        self.bl = BaseLocators()

        self.File_read_util = Filereadutil()



    def orderer_info_check(self) -> bool:
        """주문서에 표시된 주문자 정보가 로그인 회원의 프로필과 일치하는지 검증.

        로그인 상태에서는 입력 폼 대신 프로필이 텍스트로 노출된다.
        """
        try:
            profile = self.order_data.get_profile()
            assert profile, "프로필 조회 실패 → 로그인 상태가 아님"

            self.order_page.wait_orderer_view()

            assert self.check_text(self.ol.view_orderer_name, profile.get("name", "")), \
                f"주문자 이름 불일치: 기대={profile.get('name')}"
            assert self.check_text(self.ol.view_orderer_phone, profile.get("phone", "")), \
                f"주문자 연락처 불일치: 기대={profile.get('phone')}"
            assert self.check_text(self.ol.view_orderer_email, profile.get("email", "")), \
                f"주문자 이메일 불일치: 기대={profile.get('email')}"

        except AssertionError:
            logger.exception("주문자 정보 불일치: 화면=%s", self.order_page.view_orderer_info())
            return False

        except Exception:
            logger.exception("주문자 정보 검증 중 오류: url=%s", self.page.url)
            raise

        logger.info("주문자 정보 일치: %s", self.order_page.view_orderer_info())

        return True

    def delivery_info_check(self) -> bool:
        """주문서에 표시된 배송지 정보가 로그인 회원의 프로필과 일치하는지 검증.

        배송지 기본값은 프로필의 이름/연락처/주소를 그대로 사용한다.
        """
        try:
            profile = self.order_data.get_profile()
            assert profile, "프로필 조회 실패 → 로그인 상태가 아님"

            self.order_page.wait_delivery_view()

            assert self.check_text(self.ol.view_recipient, profile.get("name", "")), f"받는 사람 불일치: 기대={profile.get('name')}"
            assert self.check_text(self.ol.view_phone, profile.get("phone", "")), f"배송지 연락처 불일치: 기대={profile.get('phone')}"
            assert self.check_text(self.ol.view_address, profile.get("address", "")), f"배송지 주소 불일치: 기대={profile.get('address')}"

        except AssertionError:
            logger.exception("배송지 정보 불일치: 화면=%s", self.order_page.view_delivery_info())
            return False

        except Exception:
            logger.exception("배송지 정보 검증 중 오류: url=%s", self.page.url)
            raise

        logger.info("배송지 정보 일치: %s", self.order_page.view_delivery_info())

        return True




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




    def order_valid_check(self, field) -> bool:
        try:
            msg = self.order_data.error_msg()
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







    def ordered_info_check(self, ordered, request_text="", payment="card") -> bool:
        """생성된 주문(GET /api/orders/{id})이 프로필/요청사항/결제수단과 일치하는지 검증.

        로그인 주문은 폼을 채우지 않으므로 주문자·배송지 값이 프로필에서 와야 한다.
        """
        try:
            profile = self.order_data.get_profile()
            assert profile, "프로필 조회 실패 → 로그인 상태가 아님"

            # 주문자 정보
            assert ordered.get("orderer_name") == profile.get("name"), \
                f"주문 주문자 이름 불일치: 주문={ordered.get('orderer_name')}, 프로필={profile.get('name')}"
            assert ordered.get("orderer_phone") == profile.get("phone"), \
                f"주문 주문자 연락처 불일치: 주문={ordered.get('orderer_phone')}, 프로필={profile.get('phone')}"
            assert ordered.get("orderer_email") == profile.get("email"), \
                f"주문 주문자 이메일 불일치: 주문={ordered.get('orderer_email')}, 프로필={profile.get('email')}"

            # 배송지 정보
            assert ordered.get("recipient_name") == profile.get("name"), \
                f"주문 받는사람 불일치: 주문={ordered.get('recipient_name')}, 프로필={profile.get('name')}"
            assert ordered.get("phone") == profile.get("phone"), \
                f"주문 배송지 연락처 불일치: 주문={ordered.get('phone')}, 프로필={profile.get('phone')}"
            assert ordered.get("address") == profile.get("address"), \
                f"주문 배송지 주소 불일치: 주문={ordered.get('address')}, 프로필={profile.get('address')}"

            # 배송 요청사항 (미입력이면 빈 문자열로 저장된다)
            assert ordered.get("delivery_request") == request_text, \
                f"배송 요청사항 불일치: 주문={ordered.get('delivery_request')!r}, 기대={request_text!r}"

            # 결제수단
            assert ordered.get("payment_method") == payment, \
                f"결제수단 불일치: 주문={ordered.get('payment_method')}, 기대={payment}"

        except AssertionError:
            logger.exception("주문 내용 불일치: order_no=%s", ordered.get("order_no"))
            return False

        except Exception:
            logger.exception("주문 내용 검증 중 오류: order=%r", ordered)
            raise

        logger.info(
            "주문 내용 일치: order_no=%s 결제수단=%s 요청사항=%r",
            ordered.get("order_no"), payment, request_text
        )

        return True