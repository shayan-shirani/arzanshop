from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound
from .services import CartService
from .cart import Cart
from apps.shop.models import Product
from .serializers import CartSerializer, CartActionSerializer, DiscountSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse

class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=CartSerializer,
        responses={
            200: CartSerializer,
            400: OpenApiResponse(description='No cart found')
        }
    )
    def list(self, request):
        cart = Cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CartActionSerializer,
        responses={
            200: OpenApiResponse(description='Added to cart'),
            400: OpenApiResponse(description='No product found')
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def add(self, request):
        cart = Cart(request)
        CartService.add_to_cart(cart, request.data.get('product'))
        return Response({'message': 'Product added'}, status=status.HTTP_200_OK)

    @extend_schema(
        request=CartActionSerializer,
        responses={
            200: OpenApiResponse(description='Product decreased'),
            400: OpenApiResponse(description='No product found')
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def decrease(self, request):
        cart = Cart(request)
        CartService.decrease_product_quantity(cart, request.data.get('product_id'))
        return Response({'message': 'Product decreased'}, status=status.HTTP_200_OK)

    @extend_schema(
        request=CartActionSerializer,
        responses={
            200: OpenApiResponse(description='Product removed'),
            400: OpenApiResponse(description='No product found')
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def remove(self, request):
        cart = Cart(request)
        CartService.remove_from_cart(cart, request.data.get('product_id'))
        return Response({'message': 'Product removed'}, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            200: OpenApiResponse(description='Cart cleared')
        }
)
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def clear(self,request):
        cart = Cart(request)
        cart.clear()
        return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)

    @extend_schema(
        request=DiscountSerializer,
        responses={
            200: DiscountSerializer,
            400: OpenApiResponse(description='No discount found')
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def apply_discount(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'No discount code provided'}, status=status.HTTP_400_BAD_REQUEST)
        cart = Cart(request)
        result = cart.apply_discount(code)
        return Response(result, status=status.HTTP_200_OK)