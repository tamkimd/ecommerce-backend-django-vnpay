from django.db import models
from account.models import User
from product.models import StockProduct


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("order", "ordered"),
        ("shipping", "in transit"),
        ("success", "Order delivered and payment successful"),
        ("failed", "Order failed"),
        ("cancelled", "cancelled"),
        ("delivery_failed", "Delivery failed"),

    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_date = models.DateField(null=True)
    ordered_date = models.DateField(auto_now_add=True)
    completed_date = models.DateField(null=True)
    cancelled_date = models.DateField(null=True)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending")

    class Meta:
        db_table = "order"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "cart"


class LineItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="line_items", null=True
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="line_items", null=True
    )
    stock_product = models.ForeignKey(
        StockProduct, on_delete=models.CASCADE, null=True
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "line_item"


class Shipment(models.Model):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("success", " delivered  successful"),
        ("failed", "delivered failed"))

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shipper = models.ForeignKey(User, on_delete=models.CASCADE)
    date_shipped = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending")

    class Meta:
        db_table = "shipment"


class DeliveredItem(models.Model):
    shipment = models.ForeignKey(
        Shipment, on_delete=models.CASCADE, related_name="delivered_items")
    line_item = models.ForeignKey(LineItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = "delivered_item"


class ShippingInfo(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.IntegerField()
    note = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = "shipping_info"
