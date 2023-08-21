from django.db import models


class Product(models.Model):
    image = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    color = models.CharField(max_length=20)
    manufacturer = models.CharField(max_length=50)
    origin = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'product'


class Stock(models.Model):
    name = models.CharField(max_length=100)
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    ward = models.CharField(max_length=50)
    address_line = models.CharField(max_length=200)

    class Meta:
        db_table = 'stock'


class StockProduct(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stock_products")
    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="stock_products")
    quantity = models.IntegerField()

    class Meta:
        db_table = 'product_stock'
