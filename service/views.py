from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from order.models import Order, Promotion
from order.serializers import OrderSerializer
from .promotion import calculate_free_items
from .payment import calculate_total_refund_amount


class CalculateFreeItemsView(APIView):
    def post(self, request):
        order_id = request.data.get('order_id')

        try:
            order = Order.objects.get(pk=order_id)
            promotion = order.promotion
            print(promotion)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Promotion.DoesNotExist:
            return Response({"detail": "Promotion not found."}, status=status.HTTP_404_NOT_FOUND)

        free_items_dict = calculate_free_items(order)
        return Response(free_items_dict, status=status.HTTP_200_OK)


class CalculateRefundAmount(APIView):
    def post(self, request):
        items_dict = request.data.get('items_dict')

        total = calculate_total_refund_amount(items_dict)
        return Response(total, status=status.HTTP_200_OK)
