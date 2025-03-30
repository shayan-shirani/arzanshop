from drf_spectacular.utils import OpenApiExample

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