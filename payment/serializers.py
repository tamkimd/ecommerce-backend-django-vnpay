from rest_framework import serializers
from .models import Payment
from .vnpay import VnpayPayment
from django.db import transaction
from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'order', 'payment_amount', 'method', 'status')
        extra_kwargs = {'payment_amount': {'required': False}}

    def validate_order(self, value):
        allowed_statuses = ["pending", "in_charge"]
        if value.status not in allowed_statuses:
            raise serializers.ValidationError(
                "Payment can only be created for order with 'pending' or 'in charge' status.")
        return value

    def calculate_total_payment_amount(self, order):
        line_items = order.line_items.all()
        total_payment_amount = sum(
            line_item.price * line_item.quantity for line_item in line_items)
        return total_payment_amount

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

        validated_data["payment_amount"] = self.calculate_total_payment_amount(
            order)
        return super().create(validated_data)


class VnpayPaymentSerializer(serializers.Serializer):
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
