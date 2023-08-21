
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('api/', include('account.urls')),
    path('api/', include('product.urls')),
    path('api/', include('order.urls')),
    path('api/', include('payment.urls')),
    path('schema/', SpectacularAPIView.as_view(), name="schema"),
    path('schema/docs', SpectacularSwaggerView.as_view(url_name="schema"))
]
