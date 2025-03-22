from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views as api_views

app_name = 'cart'
router = DefaultRouter()
router.register(r'cart', api_views.CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]