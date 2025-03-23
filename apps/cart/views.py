from rest_framework import status, viewsets
from .cart import Cart
from rest_framework.decorators import action
from apps.shop.models import Product
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, OpenApiResponse, OpenApiExample, extend_schema
from rest_framework.permissions import AllowAny
from .serializers import CartSerializer, CartActionSerializer, DiscountSerializer



class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    def list(self, request):
        cart = Cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def add(self, request):
        product = self.get_product(request)
        cart = Cart(request)
        cart.add(product)
        return Response({'message': 'Product added'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def decrease(self, request):
        product = self.get_product(request)
        cart = Cart(request)
        cart.decrease(product)
        return Response({'message': 'Product decreased'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def remove(self, request):
        product = self.get_product(request)
        cart = Cart(request)
        cart.remove(product)
        return Response({'message': 'Product removed'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def clear(self,request):
        cart = Cart(request)
        cart.clear()
        return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def apply_discount(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'No discount code provided'}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart(request)
        result = cart.apply_discount(code)
        return Response(result, status=status.HTTP_200_OK)

    def get_product(self, request):
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return product