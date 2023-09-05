from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShippingInfoViewSet, OrderViewSet, CartViewSet, PromotionViewSet, LineItemViewSet, ShipmentViewSet
router = DefaultRouter()
router.register(r'shippinginfo', ShippingInfoViewSet, basename='shipping-info')
router.register(r'order', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'lineitem', LineItemViewSet, basename='line-item')
router.register(r'shipment', ShipmentViewSet, basename='shipment')
router.register(r'promotion', PromotionViewSet, basename='promotion')

urlpatterns = [
    # path('payment/create/', PaymentUrlCreateAPIView.as_view(), name='payment-create'),
    path('', include(router.urls)),
]
