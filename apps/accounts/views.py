from logging import exception

from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from .permissions import *
from rest_framework_simplejwt.exceptions import TokenError
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .selectors.user_selectors import get_all_users, get_user_by_id, get_user_by_phone, get_user_by_email
from .selectors.address_selectors import get_all_addresses, get_address_by_user
from .selectors.password_reset_selectors import get_user_by_email, get_user_by_uidb64
from .selectors.vendor_selectors import get_all_vendors, get_vendor_by_user, get_vendor_by_pk_status

from .services.jwt import JwtService
from .services.password_reset_services import PasswordResetService
from .services.login_services import validate_username, generate_request_id


import uuid
import re
from .serializers import *

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserOrAdmin]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return get_all_users()

        return get_user_by_id(user.id)

    def get_serializer_class(self):
        if self.action == 'list':
            return ShopUserSerializer

        elif self.action == 'create':
            return UserRegistrationSerializer

        elif self.action in ['update', 'partial_update']:
            return UserRegistrationSerializer

        else:
            return ShopUserDetailSerializer


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    queryset = get_all_addresses()

    def list(self, request, *args, **kwargs):
        queryset = get_address_by_user(request.user)
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
            serializer = AddressSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ChangePasswordView(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(description='Password changed successfully'),
            400: OpenApiResponse(description='Passwords do not match'),
        }
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            JwtService.token_blacklist(request.user)
            return Response({'detail':'Password changed successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(description='Reset password email sent successfully'),
            400: OpenApiResponse(description='User not found')
        }
    )
    def post(self, request):
        email = request.data.get('email')
        try:
            user = get_user_by_email(email)
        except ShopUser.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        token = PasswordResetService.generate_reset_password_token(user)
        cache.delete(f'reset_password_token:{user.pk}')
        cache.set(f'reset_password_token:{user.pk}', token, timeout=3600)

        PasswordResetService.send_reset_password_email(user, token)

        return Response({'detail': 'Reset password email sent successfully'}, status=status.HTTP_200_OK)


class PasswordResetView(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, uidb64, token):
        user = get_user_by_uidb64(uidb64)
        stored_token = cache.get(f'reset_password_token:{user.pk}')

        if not stored_token or stored_token != token:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            JwtService.token_blacklist(user)

        cache.delete(f'password_reset_token:{user.pk}')

        return Response({'detail': 'Password reset successfully.'}, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            JwtService.logout(refresh_token)
            return Response({'message': 'Logout successful!'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)

class VendorProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = VendorProfileSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return get_all_vendors()

        return get_vendor_by_user(user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        try:
            vendor = get_vendor_by_pk_status(pk, 'pending')
            vendor.approve()
            return Response({'message': 'Vendor profile approved'})
        except VendorProfile.DoesNotExist:
            return Response({'error': 'Vendor profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        try:
            vendor = get_vendor_by_pk_status(pk, 'pending')
            vendor.reject()
            return Response({'message': 'Vendor profile rejected'}, status=status.HTTP_200_OK)
        except VendorProfile.DoesNotExist:
            return Response({'error': 'Vendor profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

class LoginRequest(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(request=LoginSerializer)
    def post(self, request):
        username = request.data.get('username')
        pass_service = PasswordResetService()
        username_type = validate_username(username)
        request_id = generate_request_id()

        if username_type == 'email':
            try:
                user = get_user_by_email(username)
                cache.set(f'user_email:{request_id}', username, timeout=300)
                return Response({'message': 'Please enter your password', 'request_id':request_id}, status=status.HTTP_200_OK)
            except ShopUser.DoesNotExist:
                return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

        elif username_type == 'phone':
            try:
                user = get_user_by_phone(username)
                cache.set(f'user_phone:{request_id}', username, timeout=300)
                PasswordResetService.send_otp(user.phone, user.email)
                return Response({'message': 'OTP has been sent to your email', 'request_id':request_id}, status=status.HTTP_200_OK)
            except ShopUser.DoesNotExist:
                return Response({'error': 'Invalid phone number'}, status=status.HTTP_400_BAD_REQUEST)



class LoginVerify(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(request=LoginVerifySerializer)
    def post(self, request):
        request_id = request.data.get('request_id')
        stored_email = cache.get(f'user_email:{request_id}')
        stored_phone = cache.get(f'user_phone:{request_id}')
        password = request.data.get('password')
        if stored_email:
            try:
                user = ShopUser.objects.get(email=stored_email)

                if user.check_password(password):
                    return Response(JwtService.generate_token(user))

            except ShopUser.DoesNotExist:
                return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

        elif stored_phone:
            try:
                user = get_user_by_phone(stored_phone)
                stored_otp = cache.get(f'otp:{stored_phone}')

                if stored_otp != password:
                    return Response({'error': 'Invalid otp'}, status=status.HTTP_400_BAD_REQUEST)

                return Response(JwtService.generate_token(user))

            except ShopUser.DoesNotExist:
                return Response({'error': 'Invalid otp'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Invalid email or phone'}, status=status.HTTP_400_BAD_REQUEST)