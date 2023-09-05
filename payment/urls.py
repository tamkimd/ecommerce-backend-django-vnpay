from django.urls import path
from payment.views import CreatePaymentView,CalculateRefundAmount,RefundCreateView

# urlpatterns = [
#     path('payment/create/', CreatePaymentView.as_view(), name='payment-create'),
# ]

from django.urls import include, path
from rest_framework import routers
from .views import PaymentViewSet,CreatePaymentView,PaymentResponseAPIView

router = routers.DefaultRouter()
router.register(r'payment', PaymentViewSet)

# router.register(r'stock', StockViewSet)

urlpatterns = [

    path('', include(router.urls)),
    # path('paymentd/', PaymentView.as_view(), name='paymentv'),
    path('payment_create/', CreatePaymentView.as_view(), name='payment-create'),
    path('payment_response/', PaymentResponseAPIView.as_view(), name='payment-response'),
    path('calculate_refund/', CalculateRefundAmount.as_view(),
         name='calculate-refund'),
    path('refund/', RefundCreateView.as_view(),
         name='refund'),

]
# http://127.0.0.1:8000/api/payment_response/?vnp_Amount=10000000&vnp_BankCode=NCB&vnp_BankTranNo=VNP14081193&vnp_CardType=ATM&vnp_OrderInfo=+&vnp_PayDate=20230801073225&vnp_ResponseCode=00&vnp_TmnCode=FSTP4B3B&vnp_TransactionNo=14081193&vnp_TransactionStatus=00&vnp_TxnRef=17&vnp_SecureHash=6380b3014dcdaa474fafa7d16e54525a8cd7d3025784207dcaa1e0bbfc7a4a787bb83fd8f66c1cd80fa2afb5d5f8c8daa21280737a5eca4a23408ab6b188bf42