from rest_framework import generics, views, status, viewsets
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .cart import Cart
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary='Retrieve Cart Details',
        description='Returns the details of the cart, including items, discounts, and total prices.',
        responses={
            200: OpenApiResponse(
                description='Cart details retrieved successfully',
                examples=[
                    OpenApiExample(
                        name='Cart Example',
                        value={
                            'items': [
                                {
                                    'product': {
                                        'id': 1,
                                        'name': 'Product 1',
                                        'price': 100.0
                                    },
                                    'quantity': 2,
                                    'total_price': 200.0
                                }
                            ],
                            'discount_amount': 10.0,
                            'discount_code': 'SAVE10',
                            'post_price': 5.0,
                            'total_price': 200.0,
                            'final_price': 195.0
                        }
                    )
                ]
            )
        }
    )
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

    @extend_schema(
        summary='Add Product to Cart',
        description='Adds a product to the cart.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'product': {'type': 'integer', 'example': 1}
                },
                'required': ['product']
            }
        },
        responses={
            200: OpenApiResponse(
                description='Product added successfully',
                examples=[OpenApiExample(name='Success', value={'message': 'Product added to cart'})]
            ),
            404: OpenApiResponse(description='Product not found')
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def add(self, request):
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        cart = Cart(request)
        cart.add(product)
        return Response({'message': 'Product added to cart'}, status=status.HTTP_200_OK)
    @extend_schema(
        summary='Decrease Product Quantity in Cart',
        description='Decreases the quantity of a product in the cart.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'product': {'type': 'integer', 'example': 1}
                },
                'required': ['product']
            }
        },
        responses={
            200: OpenApiResponse(description='Product quantity decreased'),
            404: OpenApiResponse(description='Product not found')
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def decrease(self, request):
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        cart = Cart(request)
        cart.decrease(product)
        return Response({'message': 'Product decreased'}, status=status.HTTP_200_OK)
    @extend_schema(
        summary='Remove Product from Cart',
        description='Removes a product from the cart.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'product': {'type': 'integer', 'example': 1}
                },
                'required': ['product']
            }
        },
        responses={
            200: OpenApiResponse(description='Product removed from cart'),
            404: OpenApiResponse(description='Product not found')
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def remove(self, request):
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        cart = Cart(request)
        cart.remove(product)
        return Response({'message': 'Product removed'}, status=status.HTTP_200_OK)
    @extend_schema(
        summary='Clear Cart',
        description='Clears all items from the cart.',
        responses={200: OpenApiResponse(description='Cart cleared successfully')}
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def clear(self,request):
        cart = Cart(request)
        cart.clear()
        return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)
    @extend_schema(
        summary='Apply Discount Code',
        description='Applies a discount code to the cart.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string', 'example': 'SAVE10'}
                },
                'required': ['code']
            }
        },
        responses={
            200: OpenApiResponse(
                description='Discount applied successfully',
                examples=[OpenApiExample(name='Success', value={'message': 'Discount applied', 'discount_amount': 10.0})]
            ),
            400: OpenApiResponse(description='Invalid discount code')
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