from django.db import models
from account.models import User
from product.models import StockProduct


class Promotion(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    required_quantity = models.PositiveIntegerField(default=0)
    free_items_quantity = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()

    class Meta:
        db_table = "promotion"


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("order", "ordered"),
        ("shipping", "in transit"),
        ("success", "Order delivered and payment successful"),
        ("failed", "Order failed"),
        ("cancelled", "cancelled"),
        ("delivery_failed", "Delivery failed"),
        # giao hàng không thành công # giao lại 3 lần (vẫn không thành công thì cancelled) ok
        # Đơn hàng cancelled hoặc failed thì trả lại tiền nếu  đã thanh toán vnpay ok
        #  quản lý giao hàng thời gian giao và phí giao hàng : 1 đơn hàng có nhiều phiếu giao hàng(tạo 1 nhiếu thì trừ trong kho): ok
        # Thêm phần thống kê: số đơn hàng , số sản phẩm đã bán,
            # thống kê theo khoảng thời gian(năm,tháng, ngày)/
        # thống kê tồn kho , thống kê thu nhập
        # thống kê theo khoảng thời gian(năm,tháng, ngày)/
        # sản phẩm đã đặt , số lượng đã nhập, đã giao đã tra, tổng tiền nhập/bán hàng
        # người mua



        # khuyến mãi áp dụng có mã khuyến mãi (theo số lượng 10 tặng 1), (số) (ok)
        # phí giao hàng (ok)
        #
        # sale order
        # buy order
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_date = models.DateField(null=True)
    ordered_date = models.DateField(auto_now_add=True)
    completed_date = models.DateField(null=True)
    cancelled_date = models.DateField(null=True)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending")
    return_of_order = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    shipping_fee = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)
    promotion = models.ForeignKey(
        Promotion, on_delete=models.SET_NULL, null=True, blank=True)

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
    free_quantity = models.PositiveIntegerField(default=0)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "line_item"


class Shipment(models.Model):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("shipping", "shipping"),
        ("success", " delivered  successful"),
        ("failed", "delivered failed"))
    # tra hang (số lượng)
    # tra hang : bold bằng true khi khách hàng bấm trả hàng và seller .
    # phí giao hàng
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shipper = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_date = models.DateField(null=True)
    shipped_date = models.DateTimeField(null=True)
    failed_date = models.DateField(null=True)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending")
    is_return = models.BooleanField(default=False)

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
