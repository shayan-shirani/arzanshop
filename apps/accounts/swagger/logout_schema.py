from drf_spectacular.utils import OpenApiExample

LOGOUT_SUCCESS_EXAMPLE = [
    OpenApiExample(
        name='Login Success',
        value={'message': 'Logout successful.'},
    )
]

LOGOUT_ERROR_EXAMPLE = [
    OpenApiExample(
        name='Missing Token',
        value={'error': 'Refresh token is required.'},
    ),
    OpenApiExample(
        name='Invalid Token',
        value={'error': 'Invalid refresh token.'},
    )
]