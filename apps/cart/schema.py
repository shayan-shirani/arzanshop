from drf_spectacular.utils import OpenApiExample

CART_ADD_EXAMPLES = [
    OpenApiExample(
        name='Add Product Success',
        value={'message': 'Product added'},
        description='Response indicating a product was successfully added to the cart.'
    )
]

CART_DECREASE_EXAMPLES = [
    OpenApiExample(
        name='Decrease Product Quantity Success',
        value={'message': 'Product decreased'},
        description='Response indicating the quantity of a product was successfully decreased.'
    )
]

CART_REMOVE_EXAMPLES = [
    OpenApiExample(
        name='Remove Product Success',
        value={'message': 'Product removed'},
        description='Response indicating a product was successfully removed from the cart.'
    )
]

CART_CLEAR_EXAMPLES = [
    OpenApiExample(
        name='Cart Cleared Success',
        value={'message': 'Cart cleared'},
        description='Response indicating the cart was successfully cleared.'
    )
]

CART_APPLY_DISCOUNT_EXAMPLES = [
    OpenApiExample(
        name='Discount Applied Successfully',
        value={'message': 'discount code Successfully applied'},
        description='Response when a discount is successfully applied to the cart.'
    )
]

CART_APPLY_DISCOUNT_ERROR_EXAMPLES = [
    OpenApiExample(
        name='Invalid Discount Code',
        value={'error': 'Invalid discount code'},
        description='Response when an invalid or non-existent discount code is provided.'
    )
]

CART_ERROR_EXAMPLES = [
    OpenApiExample(
        name='Product Not Found',
        value={'error': 'Product does not exist'},
        description='Response when a product ID is not found in the cart.'
    )
]