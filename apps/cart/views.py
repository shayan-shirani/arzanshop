from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse
)

from .cart import Cart
from .serializers import (
    CartSerializer,
    CartActionSerializer,
    DiscountSerializer
)

from .services import CartService

from .schema import (
    CART_ADD_EXAMPLES,
    CART_CLEAR_EXAMPLES,
    CART_DECREASE_EXAMPLES,
    CART_REMOVE_EXAMPLES,
    CART_APPLY_DISCOUNT_EXAMPLES,
    CART_APPLY_DISCOUNT_ERROR_EXAMPLES,
    CART_ERROR_EXAMPLES
)

@extend_schema_view(
    list=extend_schema(
        summary='Get cart',
        description='Retrieve the current cart contents.',
        responses={200: CartSerializer},
    ),
    add=extend_schema(
        summary='Add product to cart',
        description='Add a product to the cart.',
        request=CartActionSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Product added to cart successfully.',
                examples=CART_ADD_EXAMPLES
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Product not found',
                examples=CART_ERROR_EXAMPLES
            )
        }
    ),
    decrease=extend_schema(
        summary='Decrease product quantity',
        description='Decrease the quantity of a product in the cart.',
        request=CartActionSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Product decreased successfully.',
                examples=CART_DECREASE_EXAMPLES
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Product not found',
                examples=CART_ERROR_EXAMPLES
            )
        }
    ),
    remove=extend_schema(
        summary='Remove product from cart',
        description='Remove a product from the cart.',
        request=CartActionSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Product removed successfully.',
                examples=CART_REMOVE_EXAMPLES
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Product not found',
                examples=CART_ERROR_EXAMPLES
            )
        }
    ),
    clear=extend_schema(
        summary='Clear cart',
        description='Clear the cart of all products.',
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Cart cleared successfully.',
                examples=CART_CLEAR_EXAMPLES
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Product not found',
                examples=CART_ERROR_EXAMPLES
            )
        }
    ),
    apply_discount=extend_schema(
        summary='Apply discount code',
        description='Apply a discount code to the cart.',
        request=DiscountSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Discount applied successfully',
                examples=CART_APPLY_DISCOUNT_EXAMPLES,
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description= 'Discount code not found or expired',
                examples=CART_APPLY_DISCOUNT_ERROR_EXAMPLES,
            )
        },
    )
)
class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    def list(self, request):
        cart = Cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def add(self, request):
        serializer = CartActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data.get('product')
        cart = Cart(request)
        CartService.add_to_cart(cart, product)
        return Response({'message': 'Product added'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def decrease(self, request):
        serializer = CartActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data.get('product')
        cart = Cart(request)
        CartService.decrease_product_quantity(cart, product)
        return Response({'message': 'Product decreased'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        serializer = CartActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data.get('product')
        cart = Cart(request)
        CartService.remove_from_cart(cart, product)
        return Response({'message': 'Product removed'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def clear(self,request):
        cart = Cart(request)
        cart.clear()
        return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def apply_discount(self, request):
        serializer = DiscountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data.get('code')
        cart = Cart(request)
        result = cart.apply_discount(code)
        return Response(result, status=status.HTTP_200_OK)