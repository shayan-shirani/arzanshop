from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse

from .schema import (
    PRODUCT_ID_PARAMETER,
    PRODUCT_NOT_FOUND_EXAMPLES
)

from .serializers import *
from .filters import *
from .permissions import *

@extend_schema_view(
    list=extend_schema(
        summary='List products',
        description='List all products.',
        request=ProductSerializer(many=True),
        responses={
            200: ProductSerializer(many=True),
        },
    ),
    retrieve=extend_schema(
        parameters=[PRODUCT_ID_PARAMETER],
        summary='Retrieve product',
        description='Retrieve a single product by ID.',
        request=ProductSerializer,
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Product not found',
                examples=PRODUCT_NOT_FOUND_EXAMPLES
            ),
        },
    ),
    create=extend_schema(
        summary='Create product',
        description='Create a new product.',
        request=ProductCreateSerializer,
        responses={
            201: ProductSerializer,
        },
    ),
    update=extend_schema(
        parameters=[PRODUCT_ID_PARAMETER],
        summary='Update product',
        description='Update an existing product.',
        request=ProductCreateSerializer,
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Product not found',
                examples=PRODUCT_NOT_FOUND_EXAMPLES
            ),
        },
    ),
    partial_update=extend_schema(
        parameters=[PRODUCT_ID_PARAMETER],
        summary='Partial update product',
        description='Update only a subset of fields for an existing product.',
        request=ProductCreateSerializer,
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Product not found',
                examples=PRODUCT_NOT_FOUND_EXAMPLES
            )
        }
    ),
    destroy=extend_schema(
        parameters=[PRODUCT_ID_PARAMETER],
        summary='Delete product',
        description='Delete an existing product by ID.',
        responses={
            204: OpenApiResponse(description='No Content'),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Product not found',
                examples=PRODUCT_NOT_FOUND_EXAMPLES
            )
        }
    )
)
class ProductsViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsVendor]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer