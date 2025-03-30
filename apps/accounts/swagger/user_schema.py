from drf_spectacular.utils import OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

USER_ID_PARAMETER = OpenApiParameter(
    name='id',
    description='ID of the user',
    required=True,
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
)

DUPLICATE_USER_EXAMPLES = [
    OpenApiExample(
        name='Duplicate username',
        value={'error': 'Shop User with this username already exists.'},
    ),
    OpenApiExample(
        name='Duplicate email',
        value={'error': 'Shop User with this email already exists.'},
    ),
    OpenApiExample(
        name='Phone length',
        value={'error': 'Phone number must be 11 digits.'},
    )
]

INVALID_ID_EXAMPLES = [
    OpenApiExample(
        name='Invalid ID',
        value={'error': 'No user found with the given ID.'},
    )
]

ALL_ERROR_EXAMPLES = INVALID_ID_EXAMPLES + DUPLICATE_USER_EXAMPLES
