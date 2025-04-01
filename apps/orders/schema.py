from drf_spectacular.utils import OpenApiExample

ORDER_CREATE_ERROR_EXAMPLES = [
    OpenApiExample(
        name='Failed to Initiate Payment',
        value={'error': 'Failed to initiate payment'},
        description="Response when the system fails to initiate payment after "
                    "order creation due to an issue with the payment gateway."
    ),
]
