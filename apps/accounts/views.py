from django.core.cache import cache

from rest_framework import viewsets, views, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes

from .swagger.user_schema import (
    USER_ID_PARAMETER,
    DUPLICATE_USER_EXAMPLES,
    INVALID_ID_EXAMPLES,
    ALL_ERROR_EXAMPLES
)
from .swagger.password_schema import (
    PASSWORD_CHANGE_ERRORS,
    PASSWORD_CHANGE_SUCCESS_EXAMPLES,
    PASSWORD_RESET_REQUEST_SUCCESS_EXAMPLE,
    PASSWORD_RESET_REQUEST_MISSING_EMAIL_EXAMPLE,
    PASSWORD_RESET_REQUEST_USER_NOT_FOUND_EXAMPLE,
    PASSWORD_RESET_SUCCESS_EXAMPLE,
    PASSWORD_RESET_VALIDATION,
    PASSWORD_RESET_INVALID_UID_EXAMPLE,
    PASSWORD_RESET_PARAMETERS
)
from .swagger.logout_schema import (
    LOGOUT_SUCCESS_EXAMPLE,
    LOGOUT_ERROR_EXAMPLE
)
from .swagger.vendor_schema import (
    VENDOR_REJECT,
    VENDOR_APPROVE,
    VENDOR_NOT_FOUND
)
from .swagger.login_schema import (
    PASSWORD_OTP_EXAMPLE,
    INVALID_EMAIL_PHONE_EXAMPLE,
    LOGIN_VERIFY_ERROR_EXAMPLES
)

from .selectors.user_selectors import (
    get_all_users,
    get_user_by_id,
    get_user_by_phone,
    get_user_by_email,
    get_user_by_uidb64,
)
from .selectors.address_selectors import get_address_by_user
from .selectors.vendor_selectors import (
    get_all_vendors,
    get_vendor_by_user,
    get_vendor_by_pk_status,
)

from .services.jwt import JwtService
from .services.password_reset_services import PasswordResetService
from .services.login_services import validate_username, generate_request_id

from .permissions import *

from .serializers import *


@extend_schema_view(
    list=extend_schema(
        summary='List all users',
        description='Retrieve the list of all registered users.',
        responses={200: ShopUserSerializer(many=True)},
    ),
    retrieve=extend_schema(
        parameters=[USER_ID_PARAMETER],
        summary='Retrieve a specific user',
        description='Get details of a specific user by their ID.',
        responses={200: ShopUserDetailSerializer},
    ),
    create=extend_schema(
        summary='Create a new user',
        description='Register a new user by providing necessary details.',
        request=UserRegistrationSerializer,
        responses={
            201: UserRegistrationSerializer,
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=DUPLICATE_USER_EXAMPLES,
            )
        },
    ),
    update=extend_schema(
        summary='Update user details',
        description='Update information of an existing user.',
        parameters=[USER_ID_PARAMETER],
        request=UserRegistrationSerializer,
        responses={
            200: UserRegistrationSerializer,
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=ALL_ERROR_EXAMPLES
            )
        },
    ),
    partial_update=extend_schema(
        summary='Partially update user details',
        description='Update only a subset of fields for an existing user.',
        parameters=[USER_ID_PARAMETER],
        request=UserRegistrationSerializer,
        responses={
            200: UserRegistrationSerializer,
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=ALL_ERROR_EXAMPLES
            )
        },
    ),
    destroy=extend_schema(
        summary='Delete a user',
        description='Delete an existing user by their ID.',
        parameters=[USER_ID_PARAMETER],
        responses={
            204: OpenApiResponse(description='No Content'),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=INVALID_ID_EXAMPLES,
            )
        },
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserOrAdmin]
    parser_classes = [MultiPartParser]

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

@extend_schema_view(
    list=extend_schema(
        summary='List all addresses',
        description='Retrieve the list of all addresses associated with the user.',
        responses={200: AddressSerializer(many=True)},
    ),
    retrieve=extend_schema(
        parameters=[USER_ID_PARAMETER],
        summary='Retrieve a specific address',
        description='Get details of a specific address by their ID.',
        responses={
            200: OpenApiResponse(description='No Content'),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=INVALID_ID_EXAMPLES,
            )
        }
    ),
    create=extend_schema(
        summary='Create a new address',
        description='Create a new address for the user.',
        request=AddressSerializer,
        responses={201: AddressSerializer},
    ),
    update=extend_schema(
        parameters=[USER_ID_PARAMETER],
        summary='Update an address',
        description='Update information of an existing address.',
        responses={
            200: OpenApiResponse(description='No Content'),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=INVALID_ID_EXAMPLES,
            )
        }
    ),
    partial_update=extend_schema(
        parameters=[USER_ID_PARAMETER],
        summary='Partially update an address',
        description='Update only a subset of fields for an existing address.',
        responses={
            200: OpenApiResponse(description='No Content'),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=INVALID_ID_EXAMPLES,
            )
        }
    ),
    destroy=extend_schema(
        parameters=[USER_ID_PARAMETER],
        summary='Delete an address',
        description='Delete an existing address by their ID.',
        responses={
            200: OpenApiResponse(description='No Content'),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=INVALID_ID_EXAMPLES,
            )
        }
    )
)
class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return get_address_by_user(self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = AddressSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ChangePasswordView(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Change User Password',
        description="""
            Allows an authenticated user to change their password.
            The user must provide their current password and a new password.
            If successful, the user's tokens will be blacklisted.
        """,
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Password changed successfully',
                examples=PASSWORD_CHANGE_SUCCESS_EXAMPLES
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Invalid input',
                examples=PASSWORD_CHANGE_ERRORS,
            ),
        },
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            JwtService.token_blacklist(request.user)
            return Response(
                {'detail': 'Password changed successfully'},
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class PasswordResetRequestView(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Request Password Reset",
        description="""
            Allows unauthenticated users to request a password reset. 
            The user must provide a valid email address associated with their account. 
            If the email is valid, a password reset token will be generated and emailed to the user.
        """,
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="Password reset request processed successfully.",
                examples=PASSWORD_RESET_REQUEST_SUCCESS_EXAMPLE,
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Invalid input. Missing or invalid email.",
                examples=PASSWORD_RESET_REQUEST_MISSING_EMAIL_EXAMPLE
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="User with the provided email not found.",
                examples=PASSWORD_RESET_REQUEST_USER_NOT_FOUND_EXAMPLE
            ),
        },
    )
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response(
                {'detail': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = get_user_by_email(email)
        except ShopUser.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        token = PasswordResetService.generate_reset_password_token(user)
        cache.delete(f'reset_password_token:{user.pk}')
        cache.set(f'reset_password_token:{user.pk}', token, timeout=3600)

        PasswordResetService.send_reset_password_email(user, token)

        return Response(
            {'detail': 'Reset password email sent successfully'},
            status=status.HTTP_200_OK
        )



class PasswordResetView(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary='Reset Password',
        description="""
            Allows unauthenticated users to reset their password using the `uidb64` and `token`
            sent during the password reset request. A valid token and UID must be provided,
            along with the new password in the request body.
        """,
        parameters=PASSWORD_RESET_PARAMETERS,
        request=PasswordResetSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Password reset successfully.',
                examples=PASSWORD_RESET_SUCCESS_EXAMPLE,
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Bad Request. Invalid Token, UID, or Password Validation Error.',
                examples=PASSWORD_RESET_VALIDATION
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Invalid UID or user not found.',
                examples=PASSWORD_RESET_INVALID_UID_EXAMPLE,
            ),
        }
    )
    def post(self, request, uidb64, token):
        try:
            user = get_user_by_uidb64(uidb64)
        except (TypeError, ValueError, OverflowError, ShopUser.DoesNotExist):
            raise ValueError(
                'Invalid UID or user not found.'
            )

        stored_token = cache.get(f'reset_password_token:{user.pk}')

        if not stored_token or stored_token != token:
            return Response(
                {'error': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            JwtService.token_blacklist(user)

        cache.delete(f'password_reset_token:{user.pk}')
        return Response(
            {'detail': 'Password reset successfully.'},
            status=status.HTTP_200_OK
        )


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Logout User',
        description="""
            Logout the currently authenticated user by invalidating their refresh token.
            The `refresh` token must be included in the request body.
        """,
        request=LoginSerializer,
        responses={
            205: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Successful logout response",
                examples=LOGOUT_SUCCESS_EXAMPLE
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Failed logout due to missing or invalid token",
                examples=LOGOUT_ERROR_EXAMPLE
            )
        }
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            JwtService.logout(refresh_token)
            return Response(
                {'message': 'Logout successful!'},
                status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError:
            return Response(
                {'error': 'Invalid refresh token'},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    list=extend_schema(
        summary='List All Vendor Profiles',
        description="Retrieve the list of all vendor profiles based on the user's permissions.",
        responses={
            200: VendorProfileSerializer(many=True),
        },
    ),
    retrieve=extend_schema(
        summary='Retrieve Vendor Profile',
        description='Retrieve the details of a specific vendor profile.',
        responses={
            200: OpenApiResponse(
                description='Vendor profile details',
                response=VendorProfileSerializer()
            ),
            404: OpenApiResponse(
                description='Vendor profile not found.',
                response=OpenApiTypes.OBJECT,
                examples=VENDOR_NOT_FOUND,
            ),
        },
    ),
    create=extend_schema(
        summary='Create Vendor Profile',
        description="Creating a vendor profile. Requires store name and it's description"
    ),
    update=extend_schema(
        summary='Update Vendor Profile',
        description='Updating a vendor profile. Only accessible by admin or the user.',
        request=VendorProfileSerializer,
        responses={
            200: VendorProfileSerializer,
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=VENDOR_NOT_FOUND
            )
        },
    ),
    partial_update=extend_schema(
        summary='Partially update Vendor Profile',
        description='Update only a subset of fields. Only accessible by admin or the user.',
        request=VendorProfileSerializer,
        responses={
            200: VendorProfileSerializer,
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=VENDOR_NOT_FOUND
            )
        },
    ),
    destroy=extend_schema(
        summary='Delete Vendor Profile',
        description='Delete a vendor profile. Only accessible by admin or the user.',
        responses={
            204: OpenApiResponse(description='No Content'),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=VENDOR_NOT_FOUND
            )
        },
    ),
    approve=extend_schema(
        summary='Approve Vendor Profile',
        description='Approve a pending vendor profile. Only accessible by admin users.',
        request=None,
        responses={
            200: OpenApiResponse(
                description='Vendor profile approved successfully.',
                response=OpenApiTypes.OBJECT,
                examples=VENDOR_APPROVE,
            ),
            404: OpenApiResponse(
                description='Vendor profile not found.',
                response=OpenApiTypes.OBJECT,
                examples=VENDOR_NOT_FOUND,
            ),
        },
    ),
    reject=extend_schema(
        summary='Reject Vendor Profile',
        description='Reject a pending vendor profile. Only accessible by admin users.',
        request=None,
        responses={
            200: OpenApiResponse(
                description='Vendor profile rejected successfully.',
                response=OpenApiTypes.OBJECT,
                examples=VENDOR_REJECT,
            ),
            404: OpenApiResponse(
                description='Vendor profile not found.',
                response=OpenApiTypes.OBJECT,
                examples=VENDOR_NOT_FOUND,
            ),
        },
    )
)
class VendorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = VendorProfileSerializer

    def get_permissions(self):
        if self.action in ['approve', 'reject']:
            return [IsAdminUser()]
        else:
            return [IsUserOrAdmin()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return get_all_vendors()

        return get_vendor_by_user(user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        try:
            vendor = get_vendor_by_pk_status(pk, 'pending')
            vendor.approve()
            return Response(
                {'message': 'Vendor profile approved'}
            )
        except VendorProfile.DoesNotExist:
            return Response(
                {'error': 'Vendor profile does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        try:
            vendor = get_vendor_by_pk_status(pk, 'pending')
            vendor.reject()
            return Response(
                {'message': 'Vendor profile rejected'},
                status=status.HTTP_200_OK
            )
        except VendorProfile.DoesNotExist:
            return Response(
                {'error': 'Vendor profile does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )


class LoginRequest(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary='Login Request',
        description="""
            Accepts a username (email or phone number) to initiate a login request.
            - If the username is recognized as an email, prompts the user to enter their password.
            - If the username is recognized as a phone number, initiates OTP sending to their email and phone.
        """,
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="Successful login initiation.",
                response=OpenApiTypes.OBJECT,
                examples=PASSWORD_OTP_EXAMPLE
            ),
            400: OpenApiResponse(
                description="Invalid username (email or phone).",
                response=OpenApiTypes.OBJECT,
                examples=INVALID_EMAIL_PHONE_EXAMPLE
            )
        },
    )
    def post(self, request):
        username = request.data.get('username')
        username_type = validate_username(username)
        request_id = generate_request_id()

        if username_type == 'email':
            try:
                user = get_user_by_email(username)
                cache.set(f'user_email:{request_id}', username, timeout=300)
                return Response(
                    {'message': 'Please enter your password', 'request_id': request_id},
                    status=status.HTTP_200_OK
                )
            except ShopUser.DoesNotExist:
                return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

        elif username_type == 'phone':
            try:
                user = get_user_by_phone(username)
                cache.set(f'user_phone:{request_id}', username, timeout=300)
                PasswordResetService.send_otp(user.phone, user.email)
                return Response(
                    {'message': 'OTP has been sent to your email', 'request_id': request_id},
                    status=status.HTTP_200_OK
                )
            except ShopUser.DoesNotExist:
                return Response({'error': 'Invalid phone number'}, status=status.HTTP_400_BAD_REQUEST)


class LoginVerify(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary='Login Verification',
        description="""
            Verifies a login operation based on the `request_id` and `password` values. 
            Depending on the context:
            - If the `request_id` is associated with an email (password verification is used).
            - If the `request_id` is associated with a phone number (OTP verification is used).
        """,
        request=LoginVerifySerializer,
        responses={
            200: LoginVerifySerializer,
            400: OpenApiResponse(
                description="Authentication failure or invalid input",
                response=OpenApiTypes.OBJECT,
                examples=LOGIN_VERIFY_ERROR_EXAMPLES
            )
        },
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