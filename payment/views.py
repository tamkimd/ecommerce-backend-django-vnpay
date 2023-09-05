from rest_framework.views import APIView
from rest_framework import viewsets, permissions, filters
from .models import Payment
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import VnpayPaymentSerializer, PaymentSerializer,RefundSerializer,PaymentUpdateStatusSerializer
from rest_framework import status
from common.permissions import IsSeller, IsCustomer
from django.db import transaction
from rest_framework.decorators import action



class RefundCreateView(APIView):
    def post(self, request):
        serializer = RefundSerializer(data=request.data)
        if serializer.is_valid():
            refund_payment = serializer.save()
            return Response({"message": "Refund payment created successfully", "payment_id": refund_payment.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CalculateRefundAmount(APIView):
    def post(self, request):
        serializer = RefundSerializer(data=request.data)

        if serializer.is_valid():
            total_refund_amount = serializer.validated_data['total_refund_amount']
            return Response({'total_refund_amount': total_refund_amount}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        user = self.request.user

        if IsCustomer().has_permission(self.request, self):
            query = Payment.objects.filter(order__user=user)
        elif IsSeller().has_permission(self.request, self):
            query = Payment.objects.all()
        return query

    def get_permissions(self):
        if self.action in ["list", "retrieve","update_status"]:
            permission_classes = [IsCustomer | IsSeller]
        elif self.action in ["create"]:
            permission_classes = [IsCustomer]

        else:
            permission_classes = [IsSeller]

        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        payment = self.get_object()
        serializer = PaymentUpdateStatusSerializer(
            payment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data, context={'request': request})
    #     serializer.is_valid(raise_exception=True)
    #     payment = serializer.save()
    #     method = serializer.validated_data.get("method")
    #     order = serializer.validated_data.get("order")

    #     if method == "vnpay":
    #         vnpay_data = {
    #             'payment' : payment.pk,
    #             'order_type': 'gas',
    #             'order_desc': 'vnpay',
    #             'bank_code': 'NCB',
    #             'language': 'vn'
    #         }
    #         vnpay_serializer = VnpayPaymentSerializer(data=vnpay_data, context={'request': request})
    #         if vnpay_serializer.is_valid():
    #             vnpay_payment_url = vnpay_serializer.save(payment_instance=serializer.instance)
    #             serializer.validated_data['vnpay_payment_url'] = vnpay_payment_url
    #         else:
    #             return Response({'vnpay_errors': vnpay_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CreatePaymentView(APIView):
    @transaction.atomic
    def post(self, request, format=None):
        # Pass the request context to the serializer
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
                "00": "Giao dịch thành công",
                "07": "Trừ tiền thành công, giao dịch bị nghi ngờ (liên quan tới lừa đảo, giao dịch bất thường).",
                "09": "Giao dịch không thành công do: Thẻ/Tài khoản của khách hàng chưa đăng ký dịch vụ InternetBanking tại ngân hàng.",
                "10": "Giao dịch không thành công do: Khách hàng xác thực thông tin thẻ/tài khoản không đúng quá 3 lần.",
                "11": "Giao dịch không thành công do: Đã hết hạn chờ thanh toán. Xin quý khách vui lòng thực hiện lại giao dịch.",
                "12": "Giao dịch không thành công do: Thẻ/Tài khoản của khách hàng bị khóa.",
                "13": "Giao dịch không thành công do Quý khách nhập sai mật khẩu xác thực giao dịch (OTP). Xin quý khách vui lòng thực hiện lại giao dịch.",
                "24": "Giao dịch không thành công do: Khách hàng hủy giao dịch.",
                "51": "Giao dịch không thành công do: Tài khoản của quý khách không đủ số dư để thực hiện giao dịch.",
                "65": "Giao dịch không thành công do: Tài khoản của Quý khách đã vượt quá hạn mức giao dịch trong ngày.",
                "75": "Ngân hàng thanh toán đang bảo trì.",
                "79": "Giao dịch không thành công do: KH nhập sai mật khẩu thanh toán quá số lần quy định. Xin quý khách vui lòng thực hiện lại giao dịch.",
                "99": "Các lỗi khác (lỗi còn lại, không có trong danh sách mã lỗi đã liệt kê).",
            }

            message = response_messages.get(
                vnp_response_code, "Mã lỗi không hợp lệ.")
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
