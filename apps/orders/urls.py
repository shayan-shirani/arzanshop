from django.urls import path, include
from . import views as api_views

app_name = 'orders'

urlpatterns = [
    path('create/', api_views.OrderCreateView.as_view(), name='create-order'),
    path('subscription/', api_views.SubscriptionBuyView.as_view(), name='buy-subscription'),
    path('payment/callback/', api_views.PaymentCallbackView.as_view(), name='payment-callback')
]