from locators import OrderLocators
from pages.commons.common_data import Commondata
from utilities.File_read import Filereadutil
from utilities.api import AuthApi
from utilities.logger import get_logger

logger = get_logger(__name__)

class Orderdata():
    def __init__(self, page, base_url: str):
        self.base_url = base_url
        self.page = page
        self.common_data = Commondata(base_url)
        self.read_util = Filereadutil()
        self.ol = OrderLocators()

        # 브라우저 세션 쿠키를 공유해야 로그인 상태의 /api/me 를 읽을 수 있다
        self.auth_api = AuthApi(page.request)

        # --- 로그인 상태 검증 ---

    def get_profile(self) -> dict:
        """로그인한 회원의 프로필(/api/me)을 반환. 비로그인이면 401 이라 빈 dict."""
        response = self.auth_api.me()

        if response.status != 200:
            logger.warning("프로필 조회 실패(비로그인 추정): status=%s", response.status)
            return {}

        return response.json()


    def buyer_Information(self):
        buyer_name = self.read_util.readConfig("delivery", "orderer_name")
        buyer_phone = self.read_util.readConfig("delivery", "orderer_phone")
        buyer_mail = self.read_util.readConfig("delivery", "orderer_email")

        return {"name": buyer_name, "phone": buyer_phone, "email": buyer_mail}


    def delivery_Information(self):
        reciver_name = self.read_util.readConfig("delivery", "recipient_name")
        reciver_phone = self.read_util.readConfig("delivery", "recipient_phone")
        reciver_address = self.read_util.readConfig("delivery", "shippingaddress")

        return {"recipient": reciver_name, "delivery_phone": reciver_phone, "address": reciver_address}

        # --- 내부: 필드명 → 로케이터 매핑 ---

    def error_msg(self):
        ui_json_path = self.read_util.read_filepath("config/", "ui.json")
        ui_data = self.read_util.read_file(ui_json_path)

        order_invalid_msg = ui_data.get('order', {}).get('required_field', "")

        return {
            "invalid_order_msg" : order_invalid_msg
        }



    def input_locator(self, field: str) -> str:
        mapping = {
            "orderer_name": self.ol.orderer_name,
            "orderer_phone": self.ol.orderer_phone,
            "orderer_email": self.ol.orderer_email,
            "recipient": self.ol.recipient,
            "reciver_phone": self.ol.reciver_phone,
            "address": self.ol.address,
            "request": self.ol.request,
        }
        return mapping[field]

