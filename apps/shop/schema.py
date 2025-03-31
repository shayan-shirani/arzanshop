from drf_spectacular.utils import OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

PRODUCT_ID_PARAMETER = OpenApiParameter(
    name='id',
    description='ID of the product',
    required=True,
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
)

PRODUCT_NOT_FOUND_EXAMPLES = [
    OpenApiExample(
        name='Product not found',
        value={'detail': 'Product not found'},
        description='Example response when the product ID is not found.',
    )
]