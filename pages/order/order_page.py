"""주문서 페이지 ('/order').

주문서 폼 입력/결제수단 선택/결제하기 동작과, 검증용 요소 접근자를 제공한다.
- 셀렉터는 OrderLocators 에서만 가져오고, 실제 동작은 base_page 위임 함수로 수행한다.
- 실패(검증 차단) 케이스는 프론트가 API 호출 없이 현재 페이지에 머무르며 에러를 노출한다.
"""

from __future__ import annotations
from playwright.sync_api import Page, Locator
from locators import OrderLocators, OrderCompleteLocators, BaseLocators
from pages.base_page import BasePage

class OrderPage(BasePage):
    PATH = "/order"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.ol = OrderLocators()
        self.ocl = OrderCompleteLocators()
        self.bl = BaseLocators()

    # -- 주문자 정보
    def name(self, name):
        """주문자 정보 내 이름 입력"""
        self.input_text(self.ol.orderer_name, name)

    def phone(self, phone):
        """주문자 정보 내 연락처 입력"""
        self.input_text(self.ol.orderer_phone, phone)

    def email(self, email):
        """주문자 정보 내 이메일 입력"""
        self.input_text(self.ol.orderer_email, email)


    # -- 배송지 정보
    def recipient(self, recipient):
        """배송지 정보 내 받는 사람 입력."""
        self.input_text(self.ol.recipient, recipient)

    def recive_phone(self, recive_phone):
        """배송지 정보 내 연락처 입력."""
        self.input_text(self.ol.phone, recive_phone)

    def address(self, address):
        """배송지 정보 내 주소 입력."""
        self.input_text(self.ol.address, address)

    def delivery_request(self, request: str = ""):
        """배송지 정보 내 요청사항 입력."""
        self.input_text(self.ol.request, request)


    def select_payment(self, method: str):
        """결제수단 라디오 선택. method: card / bank / easy."""
        self.get_element_by_locator(self.ol.pay(method)).check()


    def place_order(self):
        """'결제하기' 버튼 클릭."""
        self.get_element_by_locator(self.ol.place_order).click()


    # --- 내부: 필드명 → 로케이터 매핑 ---
    def input_locator(self, field: str) -> str:
        mapping = {
            "orderer_name": self.ol.orderer_name,
            "orderer_phone": self.ol.orderer_phone,
            "orderer_email": self.ol.orderer_email,
            "recipient": self.ol.recipient,
            "reciver_phone": self.ol.phone,
            "address": self.ol.address,
            "request": self.ol.request,
        }
        return mapping[field]


    def set_field(self, field: str, value: str):
        """지정한 입력 필드의 값을 새로 채운다(빈 문자열이면 비움)."""
        self.input_text(self.input_locator(field), value)


    def clear_field(self, field: str):
        """지정한 입력 필드를 비운다."""
        self.set_field(field, "")

    # --- 검증용 접근자 ---
    def error_locator(self, field: str) -> str:
        mapping = {
            "orderer_name": self.ol.orderer_name_error,
            "orderer_phone": self.ol.orderer_phone_error,
            "orderer_email": self.ol.orderer_email_error,
            "recipient": self.ol.recipient_error,
            "reciver_phone": self.ol.reciver_phone_error,
            "address": self.ol.address_error,
        }
        return mapping[field]


    def error(self, field: str) -> Locator:
        """필드별 에러 메시지 요소를 반환. field: orderer_name/orderer_phone/orderer_email."""
        return self.get_element_by_locator(self.error_locator(field))



    # --- 진입 ---
    def open_order(self):
        """주문서로 직접 진입 후 로딩 대기 (카트에 상품이 있어야 폼이 노출됨)."""
        self.open()  # base_url + PATH 로 이동
        self.wait_loaded(self.ol.loading)




    def fill_delivery(self, recipient: str, phone: str, address: str, request: str = ""):
        """배송지 정보(받는 사람/연락처/주소/요청사항) 입력."""
        self.input_text(self.ol.recipient, recipient)
        self.input_text(self.ol.phone, phone)
        self.input_text(self.ol.address, address)

        if request:
            self.input_text(self.ol.request, request)











    def complete_container(self) :
        """주문 완료 페이지의 완료 컨테이너 요소."""
        self.wait_visible(self.get_element_by_locator(self.ocl.container))


    def order_id_from_url(self) -> int:
        """현재 URL('/order/complete/{id}')에서 주문 ID 를 추출한다."""
        return int(self.page.url.rstrip("/").split("/")[-1])



