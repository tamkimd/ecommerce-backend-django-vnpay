from utils.method import hmacsha512
import urllib.parse
from common.config import VNP_VERSION, VNP_COMMAND, VNP_CURR_CODE, VNPAY_RETURN_URL, VNPAY_PAYMENT_URL, VNPAY_API_URL, VNPAY_TMN_CODE, VNPAY_HASH_SECRET_KEY
from datetime import datetime


class VnpayPayment:
    def __init__(self, order_type, order_id, order_desc, bank_code, language, payment_amount, ipaddr):
        self.order_type = order_type
        self.order_id = order_id
        self.order_desc = order_desc
        self.bank_code = bank_code
        self.language = language
        self.payment_amount = payment_amount
        self.ipaddr = ipaddr
        self.data = self.get_data()
        self.VNPAY_PAYMENT_URL = VNPAY_PAYMENT_URL
        self.VNPAY_HASH_SECRET_KEY = VNPAY_HASH_SECRET_KEY

    def get_data(self):
        data = {}
        data["vnp_Version"] = VNP_VERSION
        data["vnp_Command"] = VNP_COMMAND
        data["vnp_TmnCode"] = VNPAY_TMN_CODE
        data["vnp_Amount"] = int(self.payment_amount * 100)
        data["vnp_CurrCode"] = VNP_CURR_CODE
        data["vnp_TxnRef"] = self.order_id
        data["vnp_OrderInfo"] = self.order_desc
        data["vnp_OrderType"] = self.order_type
        data["vnp_Locale"] = "vn"
        data["vnp_BankCode"] = self.bank_code
        data["vnp_CreateDate"] = datetime.now().strftime("%Y%m%d%H%M%S")
        data["vnp_IpAddr"] = self.ipaddr
        data["vnp_ReturnUrl"] = VNPAY_RETURN_URL

        return data

    def get_secure_hash(self):
        # Sort dictionary items alphabetically by key (Python will use default alphabetical sorting)
        sorted_data = dict(sorted(self.data.items()))

        queryString = ""
        for key, val in sorted_data.items():
            queryString += f"{key}={urllib.parse.quote_plus(str(val))}&"

        # Remove the trailing '&' character
        queryString = queryString[:-1]

        return hmacsha512(self.VNPAY_HASH_SECRET_KEY, queryString)

    def make_payment_url(self):
        hashValue = self.get_secure_hash()
        url =self.VNPAY_PAYMENT_URL + "?" + urllib.parse.urlencode(self.data) + '&vnp_SecureHash=' + hashValue
        return url, hashValue