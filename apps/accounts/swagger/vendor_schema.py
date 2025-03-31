from drf_spectacular.utils import OpenApiExample

VENDOR_APPROVE = [
    OpenApiExample(
        name='Approval Success',
        value={'message': 'Vendor approved successfully.'},
        description='Example response when a vendor profile is successfully approved.',
    )
]

VENDOR_REJECT = [
    OpenApiExample(
        name='Rejection Success',
        value={'message': 'Vendor rejected successfully.'},
        description='Example response when a vendor profile is successfully rejected.',
    )
]

VENDOR_NOT_FOUND = [
    OpenApiExample(
        name='Not Found',
        value={'error': 'Vendor profile does not exist.'},
        description='Example response when the vendor profile ID is not found.',
    )
]