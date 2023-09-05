
from order.models import Order, LineItem
from product.models import StockProduct
from payment.models import Payment


class OrderStatistics:
    def __init__(self, start_date=None, end_date=None, status=None):
        self.start_date = start_date
        self.end_date = end_date
        self.status = status

    def get_total_orders(self):
        total_orders = 0
        queryset = Order.objects.all()
        if self.start_date and self.end_date:
            date_range = (self.start_date, self.end_date)
            queryset = queryset.filter(
                ordered_date__range=(self.start_date, self.end_date))
        if self.status:
            queryset = queryset.filter(status=self.status)
        total_orders = queryset.count()
        return total_orders

    def get_total_sold_products(self):
        total_purchased_products = 0
        purchased_items = LineItem.objects.filter(
            order__status='success', order__ordered_date__range=(self.start_date, self.end_date))
        for item in purchased_items:
            total_purchased_products += item.quantity

        return total_purchased_products

    def get_total_inventory(self):
        total_inventory = 0
        stock_products = StockProduct.objects.all()
        for stock_product in stock_products:
            total_inventory += stock_product.quantity
        return total_inventory

    def get_total_income(self):
        total_income = 0
        payments = Payment.objects.filter(status='paid')
        for payment in payments:
            total_income += payment.payment_amount
        return total_income

    def get_total_ordered_products(self):
        total_ordered_products = 0
        line_items = LineItem.objects.filter(
            order__ordered_date__range=(self.start_date, self.end_date)
        )
        for item in line_items:
            total_ordered_products += item.quantity
        return total_ordered_products
