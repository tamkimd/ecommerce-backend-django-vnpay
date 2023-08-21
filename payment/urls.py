from django.urls import include, path
from rest_framework import routers
from .views import PaymentViewSet, CreatePaymentView, PaymentResponseAPIView

router = routers.DefaultRouter()
router.register(r'payment', PaymentViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('payment_create/', CreatePaymentView.as_view(), name='payment-create'),
    path('payment_response/', PaymentResponseAPIView.as_view(),
         name='payment-response'),

]
