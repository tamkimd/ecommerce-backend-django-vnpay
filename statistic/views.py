from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from order.models import (
    Cart,
    DeliveredItem,
    LineItem,
    Order,
    Shipment,
    ShippingInfo,
    StockProduct,
    Promotion,
)
from payment.models import (
    Payment
)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from django.db.models import Sum
from service.statistics import OrderStatistics


class OrderStatisticsAPIView(APIView):
    def get(self, request, format=None):
        start_date_str = request.query_params.get('start_date', '')
        end_date_str = request.query_params.get('end_date', '')
        st = request.query_params.get('status', '')

        try:
            start_date = datetime.strptime(start_date_str, "%m/%d/%Y").date()
            end_date = datetime.strptime(end_date_str, "%m/%d/%Y").date()

        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        order_statistics = OrderStatistics(start_date, end_date, st)

        response_data = {
            'total_orders': order_statistics.get_total_orders(),
            'total_purchased_products': order_statistics.get_total_sold_products(),
            'total_inventory': order_statistics.get_total_inventory(),
            'total_income': order_statistics.get_total_income(),
            'total_ordered_products': order_statistics.get_total_ordered_products()
        }

        return Response(response_data, status=status.HTTP_200_OK)


class OrderCountAPIView(APIView):
    def get(self, request, format=None):
        start_date_str = request.query_params.get('start_date', '')
        end_date_str = request.query_params.get('end_date', '')
        st = request.query_params.get('status', '')

        try:
            start_date = datetime.strptime(start_date_str, "%m/%d/%Y").date()
            end_date = datetime.strptime(end_date_str, "%m/%d/%Y").date()

        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        total_orders = Order.objects.filter(
            ordered_date__range=(start_date, end_date), status=st).count()

        total_purchased_products = 0
        purchased_items = LineItem.objects.filter(
            order__status='success', order__ordered_date__range=(start_date, end_date))
        for item in purchased_items:
            total_purchased_products += item.quantity

        response_data = {
            'total_orders': total_orders,
            'total_purchased_products': total_purchased_products
        }

        return Response(response_data, status=status.HTTP_200_OK)
