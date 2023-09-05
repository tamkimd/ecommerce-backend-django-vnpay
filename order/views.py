from urllib.parse import unquote

from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsCustomer, IsSeller

from .models import Cart, LineItem, Order, Shipment, ShippingInfo, Promotion
from .serializers import (
    CartSerializer,
    LineItemCreateSerializer,
    LineItemSerializer,
    LineItemUpdateSerializer,
    OrderCreateSerializer,
    OrderReturnSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
    ShipmentSerializer,
    ShippingInfoSerializer,
    PromotionSerializer,
    ShipmentUpdateSerializer,
)


class ShippingInfoViewSet(viewsets.ModelViewSet):
    queryset = ShippingInfo.objects.all()
    serializer_class = ShippingInfoSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "user",
                        "payments__status", "payments__method"]

    def get_queryset(self):
        """Get the orders of the currently logged-in user."""
        user = self.request.user

        if IsCustomer().has_permission(self.request, self):
            query = Order.objects.filter(user=user)
        elif IsSeller().has_permission(self.request, self):
            query = Order.objects.all()
        return query

    def filter_queryset(self, queryset):
        for field in self.filterset_fields:
            value = self.request.query_params.get(field, None)
            if value:
                decoded_value = unquote(value)
                queryset = queryset.filter(**{field: decoded_value})
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        elif self.action in ["cancel", "ship", "update_order_result"]:
            return OrderUpdateSerializer
        elif self.action in ["list", "retrieve"]:
            return OrderSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsCustomer | IsSeller]
        elif self.action in ["create", "cancel", "request_return_order"]:
            permission_classes = [IsCustomer]
        else:
            permission_classes = [IsSeller]

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["patch"])
    def cancel(self, request, pk=None):
        if pk is not None:
            order = self.get_object()
            serializer = OrderUpdateSerializer(
                order, data={"status": "cancelled"})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"status": "Order cancelled"})
        else:
            return Response(
                {"error": "Must provide a valid pk value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"])
    def request_return_order(self, request):
        try:
            serializer = OrderReturnSerializer(context={"request": request})
            serializer.create(data=request.data)

            return Response({"status": "Order return request created"})
        except Exception as e:
            print(e)
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def accept_return_order(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
            line_items = LineItem.objects.filter(order=order)
            delivered_items = [
                {"line_item": line_item.id, "quantity": line_item.quantity}
                for line_item in line_items
            ]
            data = request.data.copy()
            data["delivered_items"] = delivered_items
            data["order"] = order.id
            serializer = ShipmentSerializer(
                data=data, context={"request": request})
            if not serializer.is_valid():
                raise Exception("Bad data")
            serializer.save()

            order.status = "shipping"
            order.save()

            return Response({"status": "Order return request accepted"})
        except Exception as e:
            print(e)
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def finish_return_order(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
            line_items = LineItem.objects.filter(order=order).select_related(
                "stock_product"
            )
            for item in line_items:
                stock_product = item.stock_product
                print(stock_product.quantity)
                stock_product.quantity += item.quantity
                stock_product.save()

            order.status = "success"
            order.save()

            return Response({"status": "Order return request completed"})
        except Exception as e:
            print(e)
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["patch"])
    def ship(self, request, pk=None):
        if pk is not None:
            order = self.get_object()
            serializer = OrderUpdateSerializer(
                order, data={"status": "shipping"})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"status": "Order in transit"})
        else:
            return Response(
                {"error": "Must provide a valid pk value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["patch"])
    def update_order_result(self, request, pk=None):
        if pk is not None:
            order = self.get_object()
            status = request.data.get("status")
            if status == "success":
                message = "Order delivered and payment successful"
            elif status == "failed":
                message = "Order failed"
            else:
                return Response(
                    f"Invalid status: {status}. Valid statuses are: success, failed"
                )
            serializer = OrderUpdateSerializer(order, data={"status": status})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"status": message})
        else:
            return Response(
                {"error": "Must provide a valid pk value."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CartViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        """Get the cart of the currently logged-in user."""
        user = self.request.user

        if IsCustomer().has_permission(self.request, self):
            cart = Cart.objects.filter(user=user)
        elif IsSeller().has_permission(self.request, self):
            cart = Cart.objects.all()
        return cart


class LineItemViewSet(viewsets.ModelViewSet):
    queryset = LineItem.objects.all()
    serializer_class = LineItemSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return LineItemCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return LineItemUpdateSerializer
        else:
            return LineItemSerializer

    def get_queryset(self):
        """Get the line items for the cart of the currently logged-in user."""
        user = self.request.user
        if IsCustomer().has_permission(self.request, self):
            cart = Cart.objects.get(user=user)
            line_items = LineItem.objects.filter(cart=cart)

        elif IsSeller().has_permission(self.request, self):
            line_items = LineItem.objects.all()
        return line_items

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsCustomer | IsSeller]
        elif self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsCustomer]
        else:
            permission_classes = [IsSeller]

        return [permission() for permission in permission_classes]


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return ShipmentSerializer
        elif self.action in ["cancel", "ship", "update_order_result", "failed", "success"]:
            return ShipmentUpdateSerializer
        elif self.action in ["list", "retrieve"]:
            return ShipmentSerializer

    @action(detail=True, methods=["patch"])
    def ship(self, request, pk=None):
        if pk is not None:
            order = self.get_object()
            serializer = ShipmentUpdateSerializer(
                order, data={"status": "shipping"})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"status": "Order shipping"})
        else:
            return Response(
                {"error": "Must provide a valid pk value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["patch"])
    def success(self, request, pk=None):
        if pk is not None:
            order = self.get_object()
            serializer = ShipmentUpdateSerializer(
                order, data={"status": "success"})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"status": "Order success"})
        else:
            return Response(
                {"error": "Must provide a valid pk value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["patch"])
    def failed(self, request, pk=None):
        if pk is not None:
            order = self.get_object()
            serializer = ShipmentUpdateSerializer(
                order, data={"status": "failed"})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"status": "Order failed"})
        else:
            return Response(
                {"error": "Must provide a valid pk value."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
