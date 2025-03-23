from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views as api_views

app_name = 'shop'
router = DefaultRouter()
router.register(r'vendor-products', api_views.ProductsViewSet, basename='vendor_products')

urlpatterns = [
    path('', include(router.urls)),
]