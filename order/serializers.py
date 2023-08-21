from rest_framework import serializers


from .models import ShippingInfo, Order, Cart, LineItem, Shipment, DeliveredItem
from product.models import StockProduct
from payment.serializers import PaymentSerializer
from django.conf import settings
from datetime import datetime
from rest_framework import serializers
from .models import LineItem, Cart, StockProduct
from django.db import transaction
from django.db.models import Sum


class ShippingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingInfo
        fields = ["id", "name", "address", "phone", "note"]


class LineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItem
        fields = ["id", "cart", "order", "stock_product", "quantity", "price"]


class LineItemCreateSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)
    stock_product = serializers.PrimaryKeyRelatedField(
        queryset=StockProduct.objects.all()
    )
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)

    def validate(self, attrs):
        stock_product = attrs["stock_product"]
        quantity = attrs["quantity"]

        price = stock_product.product.price
        attrs["price"] = price
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        stock_product = validated_data["stock_product"]
        quantity = validated_data["quantity"]

        cart, is_created = Cart.objects.get_or_create(user=user)

        # Check if the stock_product already exists in the cart
        line_item = LineItem.objects.filter(
            cart=cart, stock_product=stock_product).first()

        if line_item:
            # If the stock_product already exists in the cart, update the quantity
            total_quantity = quantity + line_item.quantity
            if total_quantity > stock_product.quantity:
                raise serializers.ValidationError(
                    "Quantity exceeds available stock.")
            line_item.quantity = total_quantity
            line_item.save()
        else:
            # If the stock_product does not exist in the cart, create a new LineItem
            if quantity > stock_product.quantity:
                raise serializers.ValidationError(
                    "Quantity exceeds available stock.")
            line_item = LineItem.objects.create(cart=cart, **validated_data)

        return line_item

    class Meta:
        model = LineItem
        fields = ["id", "quantity", "stock_product", "price"]


class LineItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItem
        fields = ["id", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    line_items = LineItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "created_date", "line_items"]


class OrderSerializer(serializers.ModelSerializer):
    line_items = LineItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "shipping_date", "ordered_date",
                  "status", "line_items", "user", "payments"]


class OrderCreateSerializer(serializers.ModelSerializer):
    line_items = serializers.PrimaryKeyRelatedField(
        queryset=LineItem.objects.all(), many=True
    )
    shipping_info = ShippingInfoSerializer(required=False)

    class Meta:
        model = Order
        fields = ["id", "shipping_date", "ordered_date",
                  "status", "line_items", "shipping_info"]

    def validate_line_items(self, value):
        user = self.context["request"].user
        cart = Cart.objects.get(user=user)
        user_line_items = LineItem.objects.filter(cart=cart)
        for line_item in value:
            if line_item not in user_line_items:
                raise serializers.ValidationError(
                    "Line items must be from the user's cart.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        shipping_info_data = validated_data.pop("shipping_info")
        line_items_data = validated_data.pop("line_items")

        order = Order.objects.create(user=user, **validated_data)

        if shipping_info_data:
            ShippingInfo.objects.create(order=order, **shipping_info_data)

        if line_items_data:
            for line_item in line_items_data:
                line_item.order = order
                line_item.save()

        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

    @transaction.atomic
    def update(self, instance, validated_data):

        # Update the 'status' field
        instance.status = validated_data.get("status", instance.status)

        # Update shipping_date, completed_date, or cancelled_date based on the status
        status = validated_data.get("status", instance.status)
        if status == "shipping":
            instance.shipping_date = datetime.now()
            line_items = instance.line_items.all()

            for line_item in line_items:
                stock_product = line_item.stock_product
                stock_product.quantity -= line_item.quantity
                stock_product.save()

        elif status == "success":
            instance.completed_date = datetime.now()
        elif status == "failed" or status == "cancelled":
            instance.cancelled_date = datetime.now()

        instance.save()
        return instance


class OrderStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "total_price",
            "total_quantity",
            "created_at",
            "updated_at",
        )


class DeliveredItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveredItem
        fields = ["id", "line_item", "quantity"]




class ShipmentSerializer(serializers.ModelSerializer):
    delivered_items = DeliveredItemSerializer(many=True)

    class Meta:
        model = Shipment
        fields = ["id", "order", "shipper", "delivered_items"]

    @transaction.atomic
    def create(self, validated_data):
        delivered_items_data = validated_data.pop("delivered_items")
        shipment = Shipment.objects.create(**validated_data)

        for item_data in delivered_items_data:
            line_item = item_data["line_item"]
            quantity = item_data["quantity"]

            DeliveredItem.objects.create(
                shipment=shipment, line_item=line_item, quantity=quantity)
            stock_product = line_item.stock_product
            stock_product.quantity -= quantity
            stock_product.save()
        return shipment

    def validate_delivered_items(self, delivered_items):
        order = self.initial_data.get("order")

        line_items = LineItem.objects.filter(order=order)
        line_items_ids = [item.id for item in line_items]

        delivered_quantities = {}
        for item in DeliveredItem.objects.filter(shipment__order=order):
            if item.line_item.id in delivered_quantities:
                delivered_quantities[item.line_item.id] += item.quantity
            else:
                delivered_quantities[item.line_item.id] = item.quantity

        for item in delivered_items:
            if item['line_item'].id in line_items_ids:
                line_item = item['line_item']
                quantity_delivered = delivered_quantities.get(line_item.id, 0)

                if item['quantity'] + quantity_delivered > line_item.quantity:
                    raise serializers.ValidationError(
                        f"Quantity for line item {line_item.id} exceeds available quantity.")

        return delivered_items
