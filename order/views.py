from rest_framework import viewsets, mixins
from urllib.parse import unquote
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import ShippingInfo, Order, Cart, LineItem
from .serializers import (
    ShippingInfoSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    CartSerializer,
    LineItemSerializer,
    LineItemCreateSerializer,
    LineItemUpdateSerializer,
    ShipmentSerializer,
)
from .models import Shipment

from common.permissions import IsSeller, IsCustomer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum


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
    filterset_fields = ['status', 'user',
                        'payments__status', 'payments__method']

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
        elif self.action in ["create", "cancel"]:
            permission_classes = [IsCustomer]
        else:
            permission_classes = [IsSeller]

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["patch"])
    def cancel(self, request, pk=None):
        if pk is not None:
            order = self.get_object()
            serializer = OrderUpdateSerializer(
                order, data={"status": "cancelled"}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"status": "Order cancelled"})
        else:
            return Response(
                {"error": "Must provide a valid pk value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["patch"])
    def ship(self, request, pk=None):
        if pk is not None:
            order = self.get_object()
            serializer = OrderUpdateSerializer(
                order, data={"status": "shipping"}
            )
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
            serializer = OrderUpdateSerializer(
                order, data={"status": status}
            )
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
