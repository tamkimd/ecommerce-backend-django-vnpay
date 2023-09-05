from rest_framework import serializers
from .models import Product, Stock, StockProduct

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('id', 'name', 'province', 'district', 'ward', 'address_line')

class StockProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ('id', 'product', 'stock', 'quantity')


class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ('id', 'image', 'name', 'brand', 'weight', 'color', 'manufacturer', 'origin', 'description', 'price')


class ProductListSerializer(serializers.ModelSerializer):
    stock_products = StockProductSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'brand', 'weight', 'color', 'manufacturer', 'origin','description', 'stock_products', 'price')

class ProductByProvinceSerializer(serializers.ModelSerializer):
    stock_products = StockProductSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'brand', 'weight', 'color', 'manufacturer', 'origin', 'stock', 'price')