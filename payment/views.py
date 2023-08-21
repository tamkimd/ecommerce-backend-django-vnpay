from rest_framework.views import APIView
from rest_framework import viewsets
from .models import Payment
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import VnpayPaymentSerializer, PaymentSerializer
from common.permissions import IsSeller, IsCustomer
from django.db import transaction


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        """Get the orders of the currently logged-in user."""
        user = self.request.user

        if IsCustomer().has_permission(self.request, self):
            query = Payment.objects.filter(user=user)
        elif IsSeller().has_permission(self.request, self):
            query = Payment.objects.all()
        return query

    def get_permissions(self):
        print(self.action)
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsCustomer | IsSeller]
        elif self.action in ["create"]:
            permission_classes = [IsCustomer]

        else:
            permission_classes = [IsSeller]

        return [permission() for permission in permission_classes]


class CreatePaymentView(APIView):
    @transaction.atomic
    def post(self, request, format=None):
        serializer = VnpayPaymentSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            payment_url = serializer.create(serializer.validated_data)
            return Response({"payment_url": payment_url})
        return Response(serializer.errors, status=400)


class PaymentResponseAPIView(APIView):
    @transaction.atomic
    def get(self, request, format=None):
        input_data = request.GET
        if input_data:
            vnp_transaction_no = input_data.get('vnp_TransactionNo')
            vnp_response_code = input_data.get('vnp_ResponseCode')
            vnp_secure_hash = input_data.get('vnp_SecureHash')
            order_id = input_data.get('vnp_TxnRef')

            # dict with response_code and description
            response_messages = {
                "00": "Transaction successful",
                "07": "Money deducted successfully, transaction is suspected (related to fraud, abnormal transactions).",
                "09": "Transaction not successful because: Customer's card/account has not registered for InternetBanking service at the bank.",
                "10": "Transaction not successful because: Customer did not verify the card/account information correctly more than 3 times.",
                "11": "Transaction not successful because: The payment waiting period has expired. Please re-perform the transaction.",
                "12": "Transaction not successful because: Customer's card/account is locked.",
                "13": "Transaction not successful because: You entered the wrong transaction authentication password (OTP). Please re-perform the transaction.",
                "24": "Transaction not successful because: Customer canceled the transaction.",
                "51": "Transaction not successful because: Your account does not have enough balance to perform the transaction.",
                "65": "Transaction not successful because: Your account has exceeded the daily transaction limit.",
                "75": "The payment bank is under maintenance.",
                "79": "Transaction not successful because: KH entered the payment password wrong more than the specified number of times. Please re-perform the transaction.",
                "99": "Other errors (remaining errors, not in the list of error codes listed).",
            }

            message = response_messages.get(
                vnp_response_code, "Invalid error code.")
            print(message)
            print(vnp_response_code)
            payment = Payment.objects.get(order=order_id)
            order = payment.order
            lineitems = order.line_items.all()

            # remove item from cart
            for line_item in lineitems:
                line_item.cart = None
                line_item.save()

            if vnp_response_code == "00":
                payment.status = "paid"
                order.status = "ordered"
            else:
                payment.status = "failed"
                order.status = "failed"

            payment.vnpay_response_code = vnp_response_code
            payment.vnpay_transaction_no = vnp_transaction_no
            payment.save()
            order.save()

            response_data = {
                'message': message,
                'transaction_no': vnp_transaction_no,
                'response_code': vnp_response_code
            }

            return Response(response_data, status=200)
        return Response("error input_data", status=400)
