
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('api/', include('account.urls')),
    path('api/', include('product.urls')),
    path('api/', include('order.urls')),
    path('api/', include('payment.urls')),
    path('api/', include('service.urls')),
    path('api/', include('statistic.urls')),
    path('schema/', SpectacularAPIView.as_view(), name="schema"),
    path('schema/docs', SpectacularSwaggerView.as_view(url_name="schema"))

    # path('api_schema/', get_schema_view(
    #     title='API Schema',
    #     description='Guide for the REST API'
    # ), name='api_schema'),
    # path('docs/', TemplateView.as_view(
    #     template_name='docs.html',
    #     extra_context={'schema_url':'api_schema'}
    #     ), name='swagger-ui'),
]
