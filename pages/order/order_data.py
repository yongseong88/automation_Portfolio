from pages.commons.common_data import Commondata
from utilities.File_read import Filereadutil


class Orderdata():
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.common_data = Commondata(base_url)

        self.read_util = Filereadutil()

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


