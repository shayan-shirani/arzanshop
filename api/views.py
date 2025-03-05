
from rest_framework import generics, views, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.tokens import default_token_generator
import re
import uuid
from .permissions import *
import requests
from .Filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.

from api.utils import *
redis_client = redis.Redis(host='localhost', port=6379, db=1)

PAYMENT_URL = 'https://panel.aqayepardakht.ir/api/v2/create'
VERIFY_URL = "https://panel.aqayepardakht.ir/api/v2/verify"
AQAYE_PARDAKHT_PIN = 'sandbox'
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ShopUser.objects.all()
        return ShopUser.objects.filter(id=user.id)
    def get_serializer_class(self):
        if self.action == 'list':
            return ShopUserSerializer
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

class AddAddressView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = AddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request, address_id):
        try:
            address = Addresses.objects.get(pk=address_id, user=request.user)
        except Addresses.DoesNotExist:
            return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(views.APIView):
    permission_classes = [IsAuthenticated]
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


def generate_reset_password_token(user):
    return default_token_generator.make_token(user)

def send_reset_password_email(user, token):
    uid = urlsafe_base64_encode(str(user.pk).encode())
    reset_url = f'http://127.0.0.1:8000/api/reset-password/{uid}/{token}'
    send_mail(
        subject='Password Reset Request',
        message=f'Click the link to reset your password: {reset_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

class PasswordResetRequestView(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
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

        return Response({"message": "Reset password email sent successfully"}, status=status.HTTP_200_OK)


class PasswordResetView(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = ShopUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, ShopUser.DoesNotExist):
            return Response({"error": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        stored_token = cache.get(f'reset_password_token:{user.pk}')

        if not stored_token or stored_token != token:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')

        if new_password != new_password_confirm:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        cache.delete(f'password_reset_token:{user.pk}')

        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful!"}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)

class VendorProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = VendorProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return VendorProfile.objects.all()
        return VendorProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'vendor_profile'):
            return Response({'error':'You have already requested a vendor profile'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        try:
            vendor = VendorProfile.objects.get(pk=pk, status='pending')
            vendor.approve()
            return Response({'message': 'Vendor profile approved'})
        except VendorProfile.DoesNotExist:
            return Response({'error': 'Vendor profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

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
                return Response({"message": "Please enter your password", 'request_id':request_id}, status=status.HTTP_200_OK)
            except ShopUser.DoesNotExist:
                return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)
        elif is_phone:
            try:
                user = ShopUser.objects.get(phone=username)
                cache.set(f'user_phone:{request_id}', username, timeout=300)
                send_otp(user.phone, username)
                return Response({"message": "OTP has been sent to your email", 'request_id':request_id}, status=status.HTTP_200_OK)
            except ShopUser.DoesNotExist:
                return Response({"error": "Invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)

class LoginVerify(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
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
                return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        elif stored_phone:
            try:
                password = request.data.get('password')
                user = ShopUser.objects.get(phone=stored_phone)
                stored_otp = cache.get(f'otp:{stored_phone}')
                if stored_otp != password:
                    return Response({"error": "Invalid otp"}, status=status.HTTP_400_BAD_REQUEST)
                refresh_token = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh_token),
                    'access': str(refresh_token.access_token)
                })
            except ShopUser.DoesNotExist:
                return Response({"error": "Invalid otp"}, status=status.HTTP_400_BAD_REQUEST)


        return Response({"error": "Invalid email or phone"}, status=status.HTTP_400_BAD_REQUEST)


class ProductsViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

class ProductCreateView(generics.CreateAPIView):
    permission_classes = [IsVendor]
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'vendor_profile'):
            serializer.save(vendor=user.vendor_profile)

class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    def list(self, request):
        cart = Cart(request)
        cart_items = []
        for item in cart:
            product_data = ProductSerializer(item['product']).data
            item_data = item.copy()
            item_data['product'] = product_data
            cart_items.append(item_data)
        cart_details = {
            'items': cart_items,
            'discount_amount': cart.get_discount_amount(),
            'discount_code':request.session.get('discount_code', None),
            'post_price': cart.get_post_price(),
            'total_price': cart.get_total_price(),
            'final_price': cart.get_final_price()

        }
        return Response(cart_details, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def add(self, request):
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(id__in=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        cart = Cart(request)
        cart.add(product)
        return Response({'message': 'Product added to cart'}, status=status.HTTP_200_OK)
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def decrease(self, request):
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(id__in=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        cart = Cart(request)
        cart.decrease(product)
        return Response({"message": "Product decreased"}, status=status.HTTP_200_OK)
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def remove(self, request):
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(id__in=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        cart = Cart(request)
        cart.remove(product)
        return Response({"message": "Product removed"}, status=status.HTTP_200_OK)
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def clear(self,request):
        cart = Cart(request)
        cart.clear()
        return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def apply_discount(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'No discount code provided'}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart(request)
        result = cart.apply_discount(code)

        return Response(result, status=status.HTTP_200_OK)


class OrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        amount = order.get_final_cost()

        payload = {
            "pin": AQAYE_PARDAKHT_PIN,
            "amount": amount,
            "callback": "http://127.0.0.1:8000/api/payment/callback/",
        }
        response = requests.post(PAYMENT_URL, json=payload)
        data = response.json()

        if data.get("status") == "success":
            transid = data.get("transid")
            order.transaction_id = transid
            order.save()
            payment_url = f"https://panel.aqayepardakht.ir/startpay/sandbox/{data.get('transid')}"
            return Response(
                {"order_id": order.id, "amount": amount, "payment_url": payment_url},
                status=status.HTTP_201_CREATED,
            )

        return Response({"error": "Failed to initiate payment"}, status=status.HTTP_400_BAD_REQUEST)


class PaymentCallbackView(views.APIView):
    def post(self, request):
        transid = request.data.get("transid")
        status_code = request.data.get("status")
        try:
            order = Order.objects.get(transaction_id=transid)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if status_code == "1":
            payload = {
                "pin": AQAYE_PARDAKHT_PIN,
                "amount": order.get_final_cost(),
                "transid": transid
            }
            response = requests.post(VERIFY_URL, json=payload)
            data = response.json()

            if data.get("status") == "success":
                order.paid = True
                order.save()
                return Response({"message": "Payment successful"})

        return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)