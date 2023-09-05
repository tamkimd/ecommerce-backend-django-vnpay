from django.db import models
from order.models import Order

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ("cash", "Pay by cash"),
        ("vnpay", "Pay with VNPAY"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("unpaid", "Unpaid"),
        ("in_charge", "In Charge"),
        ("paid", "Paid"),
        ("fail", "Fail"),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default="cash")
    payment_date = models.DateField(null=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="unpaid")
    vnpay_response_code = models.CharField(max_length=2, null=True)
    vnpay_transaction_no = models.CharField(max_length=10, null=True)
    vnpay_secure_hash = models.CharField(max_length=256, null=True)
    is_refund = models.BooleanField(default=False) 

    class Meta:
        db_table = "payment"


# hoàn trả tiền/hàng : toàn phần/từng phần