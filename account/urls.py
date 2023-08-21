from rest_framework import routers
from django.urls import path, include
from .views import register, RoleViewSet, user_login, refresh_token,forgot_password,reset_password

router = routers.DefaultRouter()
router.register(r'role', RoleViewSet)

urlpatterns = [

    path('', include(router.urls)),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('token/refresh/', refresh_token, name='refresh_token'),

    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
]
