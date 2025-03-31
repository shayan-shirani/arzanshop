from drf_spectacular.utils import OpenApiExample

PASSWORD_OTP_EXAMPLE = [
    OpenApiExample(
        name='Prompt Password',
        value={'message': 'Please enter your password', 'request_id': 'abc12345'},
        description='Response when the provided username is a valid email and a password is required.'
    ),
    OpenApiExample(
        name='OTP Sent',
        value={'message': 'OTP has been sent to your email', 'request_id': 'def67890'},
        description='Response when the provided username is a valid phone number and an OTP is sent.'
    )
]

INVALID_EMAIL_PHONE_EXAMPLE = [
    OpenApiExample(
        name='Invalid Email',
        value={'error': 'Invalid email'},
        description='Response when the email is not found in the system.'
    ),
    OpenApiExample(
        name='Invalid Phone',
        value={'error': 'Invalid phone number'},
        description='Response when the phone number is not found in the system.'
    )
]

LOGIN_VERIFY_ERROR_EXAMPLES = [
    OpenApiExample(
        name='Invalid Password Response',
        value={'error': 'Invalid password'},
        description='Response when the provided password for email verification is incorrect.'
    ),
    OpenApiExample(
        name='Invalid OTP Response',
        value={'error': 'Invalid otp'},
        description='Response when the provided OTP for phone number verification is incorrect.'
    ),
    OpenApiExample(
        name='Invalid Email or Phone Response',
        value={'error': 'Invalid email or phone'},
        description='Response when neither a valid email nor phone is found for the given request ID.'
    )
]
