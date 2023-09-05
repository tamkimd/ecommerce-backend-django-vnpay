from rest_framework import serializers
from .models import Payment
from .vnpay import VnpayPayment
from django.db import transaction
from rest_framework import serializers
from .models import Payment
from order.models import Order
from service.payment import check_refund_condition, calculate_total_refund_amount
from service.promotion import calculate_free_items
from order.models import LineItem


class RefundSerializer(serializers.ModelSerializer):
    items_dict = serializers.DictField(write_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'order', 'method', 'is_refund', 'items_dict')

    def validate(self, data):
        items_dict = data.get('items_dict', {})
        total_refund_amount = calculate_total_refund_amount(items_dict)
        data['total_refund_amount'] = total_refund_amount
        return data

    def create(self, validated_data):
        order = validated_data["order"]

  
        print(order)
        if not check_refund_condition(order):
            raise serializers.ValidationError(
                "Order is not eligible for refund")
        calculate_total_refund_amount

        total_refund_amount = validated_data["total_refund_amount"]
        payment = Payment.objects.create(
            order=order,
            payment_amount=total_refund_amount,  
            method=validated_data["method"],
            status="unpaid", 
            is_refund=True
        )

        return payment

class PaymentUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'status')
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'order', 'payment_amount',
                  'method', 'status')
        extra_kwargs = {'payment_amount': {'required': False}}

    def validate_order(self, value):
        allowed_statuses = ["pending", "in_charge"]
        if value.status not in allowed_statuses:
            raise serializers.ValidationError(
                "Payment can only be created for order with 'pending' or 'in charge' status.")
        return value

    def calculate_total_payment_amount(self, order):
        shipping_fee = order.shipping_fee
        line_items = order.line_items.all()
        total_lineitems_amount = sum(
            line_item.price * line_item.quantity for line_item in line_items
        )

        if (order.promotion.discount_percentage) != 0.00:
            line_items = order.line_items.all()
            discount_percent = order.promotion.discount_percentage
            return total_lineitems_amount * (discount_percent / 100) + shipping_fee

        return total_lineitems_amount + shipping_fee

    def add_free_item(self, order):
        free_item_dict = calculate_free_items(order)
        print(free_item_dict)
        for line_item_id, free_quantity in free_item_dict.items():
            line_item = LineItem.objects.get(id=line_item_id)

            line_item.free_quantity = free_quantity
            line_item.save()

        return order

    @transaction.atomic
    def create(self, validated_data):

        method = validated_data.get("method")
        order = validated_data.get("order")

        if method == "cash":
            # remove item in cart
            lineitems = order.line_items.all()
            print(lineitems)
            for line_item in lineitems:
                line_item.cart = None
                line_item.save()
            # status of order has changed to "ordered"
            order.status = "ordered"
            order.save()
            # status of payment == "unpaid"
        else:
            # status of order  =="pending"
            # status of payment == "in charge"
            validated_data["status"] = "in charge"
        if order.promotion.required_quantity != 0.00 and order.promotion.free_items_quantity != 0.00:
            order = self.add_free_item(order)
        validated_data["payment_amount"] = self.calculate_total_payment_amount(
            order)
        return super().create(validated_data)


class VnpayPaymentSerializer(serializers.Serializer):
    # order_id = serializers.IntegerField()
    payment = serializers.PrimaryKeyRelatedField(
        queryset=Payment.objects.all(), required=False)
    order_type = serializers.CharField(default='gas')
    order_desc = serializers.CharField(default='vnpay')
    bank_code = serializers.CharField(default='NCB')
    language = serializers.CharField(default='vn')

    class Meta:
        fields = ('payment', 'order_type',
                  'order_desc', 'bank_code', 'language')

    def get_ipaddr(self, obj):
        # Get the user's IP address from the request
        request = self.context.get('request')
        user_ip = request.META.get('REMOTE_ADDR', '')
        return user_ip

    @transaction.atomic
    def create(self, validated_data):
        ipaddr = self.get_ipaddr(validated_data)
        validated_data['ipaddr'] = ipaddr
        payment = validated_data.pop('payment')
        order = payment.order
        validated_data['order_id'] = payment.order.pk
        validated_data['payment_amount'] = payment.payment_amount
        try:
            vnpay_payment = VnpayPayment(**validated_data)
            payment_url, secure_hash = vnpay_payment.make_payment_url()
        except Exception as e:
            raise serializers.ValidationError(
                f"Error occurred while making the payment URL: {str(e)}")

        try:
            # payment = Payment.objects.filter(order_id=order.pk)
            payment.vnpay_secure_hash = secure_hash
            payment.save()
        except Payment.DoesNotExist:
            raise serializers.ValidationError(
                f"Payment with order id ={order} does not exist")

        return payment_url


# class PaymentSerializer(serializers.ModelSerializer):
#     vnpay_payment_url = serializers.SerializerMethodField()

#     class Meta:
#         model = Payment
#         fields = ('id', 'order', 'payment_amount', 'method', 'status', 'vnpay_payment_url')
#         extra_kwargs = {'payment_amount': {'required': False}}

#     def validate_order(self, value):
#         allowed_statuses = ["pending", "in_charge"]
#         if value.status not in allowed_statuses:
#             raise serializers.ValidationError(
#                 "Payment can only be created for order with 'pending' or 'in charge' status.")
#         return value

#     def calculate_total_payment_amount(self, order):
#         line_items = order.line_items.all()
#         total_payment_amount = sum(
#             line_item.price * line_item.quantity for line_item in line_items)
#         return total_payment_amount

#     def get_ipaddr(self, obj):
#         # Get the user's IP address from the request
#         request = self.context.get('request')
#         user_ip = request.META.get('REMOTE_ADDR', '')
#         return user_ip

#     def get_vnpay_payment_url(self, payment):
#         if payment.method == "vnpay":
#             try:
#                 vnpay_payment = VnpayPayment(
#                     order_id=payment.order.pk,
#                     payment_amount=payment.payment_amount,
#                     order_type='gas',  # Các giá trị mặc định tùy theo yêu cầu của bạn
#                     order_desc='',
#                     bank_code='NCB',
#                     language='vn',
#                     ipaddr='127.0.0.1'  # IP của người dùng
#                 )
#                 payment_url, _ = vnpay_payment.make_payment_url()
#                 return payment_url
#             except Exception as e:
#                 raise serializers.ValidationError(
#                     f"Error occurred while making the payment URL: {str(e)}")
#         return None


#     @transaction.atomic
#     def create(self, validated_data):
#         method = validated_data.get("method")
#         order = validated_data.get("order")

#         if method == "cash":
#             # remove item in cart
#             lineitems = order.line_items.all()
#             for line_item in lineitems:
#                 line_item.cart = None
#                 line_item.save()
#             # status of order has changed to "ordered"
#             order.status = "ordered"
#             order.save()
#             # status of payment == "unpaid"
#         else:
#             # status of order  =="pending"
#             # status of payment == "in charge"
#             validated_data["status"] = "in charge"

#         validated_data["payment_amount"] = self.calculate_total_payment_amount(
#             order)

#         # Truyền các tham số cần thiết cho khởi tạo VnpayPayment
#         vnpay_data = {
#             "order_id": order.pk,
#             "payment_amount": validated_data["payment_amount"],
#             "order_type": "gas",
#             "order_desc": "",
#             "bank_code": "NCB",
#             "language": "vn",
#             "ipaddr": self.get_ipaddr(validated_data)
#         }

#         try:
#             vnpay_payment = VnpayPayment(**vnpay_data)
#             payment_url, secure_hash = vnpay_payment.make_payment_url()
#             validated_data['vnpay_secure_hash'] = secure_hash
#             # Tiếp tục xử lý dữ liệu và lưu vào database
#             payment = super().create(validated_data)
#             return payment
#         except Exception as e:
#             raise serializers.ValidationError(
#                 f"Error occurred while making the payment URL: {str(e)}")
