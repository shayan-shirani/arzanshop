from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views as api_views

app_name = 'orders'

router = DefaultRouter()
router.register(r'orders', api_views.OrderViewSet, basename='orders')
router.register(r'subscriptions', api_views.SubscriptionViewSet, basename='subscriptions')

urlpatterns = [
    path('', include(router.urls)),
    path('payment/callback/', api_views.PaymentCallbackView.as_view(), name='payment-callback')
]