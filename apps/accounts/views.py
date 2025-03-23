from rest_framework import generics, views, status, viewsets
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from rest_framework.decorators import action
from rest_framework_simplejwt.exceptions import TokenError
from .utils import *
import uuid
import re
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework.response import Response
from .serializers import *

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ShopUser.objects.all()
        return ShopUser.objects.filter(id=user.id)
    def get_serializer_class(self):
        if self.action == 'list':
            return ShopUserSerializer
        elif self.action == 'create':
            return UserRegistrationSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserRegistrationSerializer
        else:
            return ShopUserDetailSerializer
    def perform_update(self, serializer):
        user = self.request.user
        if not user.is_staff and serializer.instance != user:
            raise PermissionDenied('You can only update your own account')
        serializer.save()
    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_staff and instance != user:
            raise PermissionDenied('You can only destroy your own account')
        instance.delete()


class UserRegistrationAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = ShopUser.objects.all()
    serializer_class = UserRegistrationSerializer

class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    queryset = Addresses.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = Addresses.objects.filter(user=request.user)
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
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'old_password': {
                        'type': 'string',
                        'example': 'oldpassword123'
                    },
                    'new_password': {
                        'type': 'string',
                        'example': 'newpassword456'
                    }
                },
                'required': ['old_password', 'new_password']
            }
        },
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Password successfully changed',
                examples=[OpenApiExample(name='Success example', value={'message': 'Password changed successfully'})]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Invalid password input or validation failed',
                examples=[OpenApiExample(name='Error example', value={'error': 'Invalid password input'})]
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Failed to blacklist old tokens',
                examples=[OpenApiExample(name='Error example', value={'error': 'Failed to blacklist old tokens'})]
            ),
        },
        summary='Change Password',
        description='old and new password required for password change'
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            try:
                tokens = OutstandingToken.objects.filter(user=request.user)
                for token in tokens:
                    BlacklistedToken.objects.get_or_create(token=token)
            except Exception:
                return Response({'error': 'Failed to blacklist old tokens'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'message':'Password changed successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'example': 'user@example.com'
                    }
                },
                'required': ['email']
            }
        },
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Password reset email sent successfully',
                examples=[OpenApiExample(name='Success example', value={'message': 'Reset password email sent successfully'})]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Invalid email format',
                examples=[OpenApiExample(name='Error example', value={'error': 'Invalid email format'})]
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='User not found',
                examples=[OpenApiExample(name='Error example', value={'error': 'User not found'})]
            ),
        },
        summary='Request Password Reset',
        description='Username required for reset password request',
    )
    def post(self, request):
        email = request.data.get('email')
        try:
            user = ShopUser.objects.get(email=email)
        except ShopUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        token = generate_reset_password_token(user)
        cache.delete(f'reset_password_token:{user.pk}')
        cache.set(f'reset_password_token:{user.pk}', token, timeout=3600)

        send_reset_password_email(user, token)

        return Response({'message': 'Reset password email sent successfully'}, status=status.HTTP_200_OK)


class PasswordResetView(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    @extend_schema(
        request={
            'application/json': {
               'type': 'object',
                'properties': {
                    'new_password': {
                        'type': 'string',
                        'example': 'newpassword123'
                    },
                    'new_password_confirm': {
                        'type': 'string',
                        'example': 'newpassword123'
                    }
                },
                'required': ['new_password', 'new_password_confirm']
            }
        },
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Password reset successfully',
                examples=[OpenApiExample(name='Success example', value={'message': 'Password reset successfully.'})]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Invalid request or token issues',
                examples=[
                    OpenApiExample(name='Error example (invalid token)', value={'error': 'Invalid or expired token.'}),
                    OpenApiExample(name='Error example (password mismatch)', value={'error': 'Passwords do not match.'}),
                    OpenApiExample(name='Error example (invalid reset link)', value={'error': 'Invalid reset link.'}),
                ]
            ),
        },
        summary='Reset Password',
        description='request id and password required for reset password',
    )
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = ShopUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, ShopUser.DoesNotExist):
            return Response({'error': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        stored_token = cache.get(f'reset_password_token:{user.pk}')

        if not stored_token or stored_token != token:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')

        if new_password != new_password_confirm:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        cache.delete(f'password_reset_token:{user.pk}')

        return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'refresh': {
                        'type': 'string',
                        'example': 'your_refresh_token_here'
                    }
                },
                'required': ['refresh']
            }
        },
        responses={
            205: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Logout successful',
                examples=[OpenApiExample(name='Success example', value={'message': 'Logout successful!'})]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Invalid or missing refresh token',
                examples=[OpenApiExample(name='Error example (missing token)', value={'error': 'Refresh token is required'}),
                          OpenApiExample(name='Error example (invalid token)', value={'error': 'Invalid refresh token'})]
            ),
        },
        summary='Logout',
        description='Log out by invalidating the refresh token.'
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
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
            return VendorProfile.objects.all()
        return VendorProfile.objects.filter(user=user)
    @extend_schema(
        request = None,
        responses ={
            200:OpenApiResponse(response=OpenApiTypes.OBJECT,description='approve vendor profile',examples=[OpenApiExample(name='reject vendor profile',value={'message':'Vendor profile approved','success':True})]),
            400:OpenApiResponse(response=OpenApiTypes.OBJECT,description='approve vendor profile',examples=[OpenApiExample(name='reject vendor profile',value={'error':'Vendor profile does not exist','success':False})]),
        },
        summary='Approve Vendor',
        description='Approve a vendor profile after validation.',
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        try:
            vendor = VendorProfile.objects.get(pk=pk, status='pending')
            vendor.approve()
            return Response({'message': 'Vendor profile approved'})
        except VendorProfile.DoesNotExist:
            return Response({'error': 'Vendor profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
    @extend_schema(
        request = None,
        responses ={
            200:OpenApiResponse(response=OpenApiTypes.OBJECT,description='reject vendor profile',examples=[OpenApiExample(name='reject vendor profile',value={'message':'Vendor profile rejected','success':True})]),
            400:OpenApiResponse(response=OpenApiTypes.OBJECT,description='reject vendor profile',examples=[OpenApiExample(name='reject vendor profile',value={'error':'Vendor profile does not exist','success':False})]),
        },
        summary='Reject Vendor',
        description='Reject a vendor profile after validation.',
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        try:
            vendor = VendorProfile.objects.get(pk=pk, status='pending')
            vendor.reject()
            return Response({'message': 'Vendor profile rejected'}, status=status.HTTP_200_OK)
        except VendorProfile.DoesNotExist:
            return Response({'error': 'Vendor profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

class LoginRequest(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    @extend_schema(
        request={
            'application/json':{
                'type':'object',
                'properties':{
                    'username':{
                        'type':'string',
                        'example':'user@example.com or +989123456789'
                    }
                },
            'required':['username']
            }
        },
        responses={
            200: OpenApiResponse(response=OpenApiTypes.OBJECT,
                                 description='Successful login request',
                                 examples=[OpenApiExample(name='Success example',value={'message':'please enter your password', 'request_id':'63609e6d-b467-4193-a333-728e71baba75'})]),
            400: OpenApiResponse(response=OpenApiTypes.OBJECT,
                                 description='Invalid password',
                                 examples=[OpenApiExample(name='Error example',value={'Error':'Invalid email or phone number'})]),
        },
        summary='Login Request',
        description='Send an email or phone number, if the user exists, they will receive a response with a request_id.'
                    'If it is an email, they proceed with a password.If it is a phone number, an OTP is sent.'
    )
    def post(self, request):
        username = request.data.get('username')
        regex_email = r'^[a-zA-Z]+([._][a-zA-Z0-9]+)*@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'
        regex_phone = r'^(\+98|98|0)9\d{9}$'
        is_email = re.match(regex_email, username)
        is_phone = re.match(regex_phone, username)
        request_id = uuid.uuid4()
        if is_email:
            try:
                user = ShopUser.objects.get(email=username)
                cache.set(f'user_email:{request_id}', username, timeout=300)
                return Response({'message': 'Please enter your password', 'request_id':request_id}, status=status.HTTP_200_OK)
            except ShopUser.DoesNotExist:
                return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
        elif is_phone:
            try:
                user = ShopUser.objects.get(phone=username)
                cache.set(f'user_phone:{request_id}', username, timeout=300)
                send_otp(user.phone, username)
                return Response({'message': 'OTP has been sent to your email', 'request_id':request_id}, status=status.HTTP_200_OK)
            except ShopUser.DoesNotExist:
                return Response({'error': 'Invalid phone number'}, status=status.HTTP_400_BAD_REQUEST)

class LoginVerify(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    @extend_schema(
        request={
            'application/json':{
                'type':'object',
                'properties':{
                    'request_id':{
                        'type':'string',
                        'example':'63609e6d-b467-4193-a333-728e71baba75'
                    },
                    'password':{
                        'type':'string',
                        'example':'user_password_or_otp'
                    }
                },
            'required':['request_id', 'password']
            }
        },
        responses={
            200: OpenApiResponse(response=OpenApiTypes.OBJECT,
                                 description='Successful login verification',
                                 examples=[OpenApiExample(name='Success example',value={'refresh': 'your_refresh_token','access': 'your_access_token'})]),
            400: OpenApiResponse(response=OpenApiTypes.OBJECT,
                                 description='Invalid email or phone number',
                                 examples=[OpenApiExample(name='Error example',value={'Error':'Invalid password'})]),
        },
        summary='Login Verification',
        description='Verify login with password (for email users) or OTP (for phone users). If successful, returns JWT tokens.'
    )
    def post(self, request):
        request_id = request.data.get('request_id')
        stored_email = cache.get(f'user_email:{request_id}')
        stored_phone = cache.get(f'user_phone:{request_id}')
        password = request.data.get('password')
        if stored_email:
            try:
                user = ShopUser.objects.get(email=stored_email)
                if user.check_password(password):
                    refresh_token = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh_token),
                        'access': str(refresh_token.access_token)
                    })
            except ShopUser.DoesNotExist:
                return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        elif stored_phone:
            try:
                password = request.data.get('password')
                user = ShopUser.objects.get(phone=stored_phone)
                stored_otp = cache.get(f'otp:{stored_phone}')
                if stored_otp != password:
                    return Response({'error': 'Invalid otp'}, status=status.HTTP_400_BAD_REQUEST)
                refresh_token = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh_token),
                    'access': str(refresh_token.access_token)
                })
            except ShopUser.DoesNotExist:
                return Response({'error': 'Invalid otp'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Invalid email or phone'}, status=status.HTTP_400_BAD_REQUEST)