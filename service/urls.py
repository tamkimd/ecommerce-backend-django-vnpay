from django.urls import path
from .views import CalculateFreeItemsView, CalculateRefundAmount

urlpatterns = [
    path('calculate-free-items/', CalculateFreeItemsView.as_view(),
         name='calculate-free-items'),
    path('calculate-refund-amount/', CalculateRefundAmount.as_view(),
         name='calculate-refund-amount'),
]
