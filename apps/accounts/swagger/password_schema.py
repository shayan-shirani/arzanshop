from drf_spectacular.utils import OpenApiExample, OpenApiParameter

PASSWORD_CHANGE_ERRORS = [
    OpenApiExample(
        name='Invalid Current Password',
        value={'current_password': 'The current password is incorrect.'},
    ),
    OpenApiExample(
        name='Weak Password',
        value={'new_password': 'This password is too weak.'},
    ),
]

PASSWORD_CHANGE_SUCCESS_EXAMPLES = [
    OpenApiExample(
        name='Success',
        value={'detail': 'Password changed successfully.'},
    )
]

PASSWORD_RESET_REQUEST_SUCCESS_EXAMPLE = [
    OpenApiExample(
        name='Successful Request',
        value={'detail': 'Reset password email sent successfully'}
    )
]

PASSWORD_RESET_REQUEST_MISSING_EMAIL_EXAMPLE = [
    OpenApiExample(
        name='Missing Email',
        value={'detail': 'Email is required'}
    )
]

PASSWORD_RESET_REQUEST_USER_NOT_FOUND_EXAMPLE = [
    OpenApiExample(
        name='User Not Found',
        value={'detail': 'User not found'}
    )
]

PASSWORD_RESET_SUCCESS_EXAMPLE = [
    OpenApiExample(
        name='Successful Reset',
        value={'detail': 'Password reset successfully.'},
    )
]

PASSWORD_RESET_INVALID_UID_EXAMPLE = [
    OpenApiExample(
        name='Invalid UID or User Not Found',
        value={'detail': 'Invalid UID or user not found.'},
    )
]

PASSWORD_RESET_INVALID_TOKEN_EXAMPLE = [
    OpenApiExample(
        name='Invalid or Expired Token',
        value={'detail': 'Invalid or expired token.'},
    )
]

PASSWORD_RESET_VALIDATION_ERROR_EXAMPLE = [
    OpenApiExample(
        name='Validation Error',
        value={'new_password': 'This password is too short. It must contain at least 8 characters.'},
    )
]

PASSWORD_RESET_VALIDATION = PASSWORD_RESET_VALIDATION_ERROR_EXAMPLE + PASSWORD_RESET_INVALID_TOKEN_EXAMPLE

PASSWORD_RESET_PARAMETERS = [
    OpenApiParameter(
        name='uidb64',
        description='The Base64 encoded UID of the user.',
        location=OpenApiParameter.PATH,
    ),
    OpenApiParameter(
        name='token',
        description="The password reset token sent to the user's email.",
        location=OpenApiParameter.PATH,
    ),
]


