from django.urls import path
from .views import OrderCountAPIView,OrderStatisticsAPIView

urlpatterns = [
    path('order-count/', OrderCountAPIView.as_view(),
         name='calculate-free-items'),
    path('statistic/order/', OrderStatisticsAPIView.as_view(),
         name='statistic-order'),
 
]
