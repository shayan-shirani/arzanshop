from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views as api_views
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'accounts'
router = DefaultRouter()
router.register(r'vendor-profiles', api_views.VendorProfileViewSet, basename='vendor_profile')
router.register(r'addresses', api_views.AddressViewSet, basename='addresses')
router.register(r'users', api_views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', api_views.LoginRequest.as_view(), name='login-request'),
    path('login-verify/', api_views.LoginVerify.as_view(), name='login-verify'),
    path('change-password/', api_views.ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', api_views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/<uidb64>/<token>/', api_views.PasswordResetView.as_view(), name='password-reset'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path("logout/", api_views.LogoutView.as_view(), name="logout"),
]
