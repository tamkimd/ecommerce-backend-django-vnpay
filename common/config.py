VNP_VERSION = "2.1.0"
VNP_COMMAND = "pay"
VNP_CURR_CODE = "VND"
VNPAY_RETURN_URL = 'http://127.0.0.1:8000/api/payment_response/'  # get from config
VNPAY_PAYMENT_URL = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'  # get from config
VNPAY_API_URL = 'https://sandbox.vnpayment.vn/merchant_webapi/api/transaction'
VNPAY_TMN_CODE = 'FSTP4B3B'  # Website ID in VNPAY System, get from config
VNPAY_HASH_SECRET_KEY = 'QRLIYJGGGPJYMIBOYXZZNJEJLXGHRPTF'  # Secret key for create checksum,get from config
