from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, StockViewSet, StockProductViewSet

router = DefaultRouter()
router.register(r'product', ProductViewSet)
router.register(r'stock', StockViewSet)
router.register(r'stockproduct', StockProductViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
