from rest_framework import viewsets,permissions
from .models import Product, Stock, StockProduct
from .serializers import ProductSerializer, ProductListSerializer, StockSerializer, StockProductSerializer
from common.permissions import IsCustomer, IsSeller
from rest_framework.filters import SearchFilter, OrderingFilter

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['brand', 'weight']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductListSerializer
        return ProductSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsSeller]

        return [permission() for permission in permission_classes]


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsSeller]

        return [permission() for permission in permission_classes]


class StockProductViewSet(viewsets.ModelViewSet):
    queryset = StockProduct.objects.all()
    serializer_class = StockProductSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsSeller]

        return [permission() for permission in permission_classes]
