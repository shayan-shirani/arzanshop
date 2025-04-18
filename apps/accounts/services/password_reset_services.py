from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings

import random
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=1)


class PasswordResetService:
    @staticmethod
    def generate_reset_password_token(user):
        return default_token_generator.make_token(user)

    @staticmethod
    def send_reset_password_email(user, token):
        uid = urlsafe_base64_encode(str(user.pk).encode())
        reset_url = f'http://127.0.0.1:8000/api/accounts/password-reset/{uid}/{token}'
        send_mail(
            subject='Password Reset Request',
            message=f'Click the link to reset your password: {reset_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    @staticmethod
    def send_otp(phone, email):
        otp = str(random.randint(100000, 999999))
        cache.set(f'otp:{phone}', otp, timeout=300)
        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP is: {otp}. It is valid for 5 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return otp

    @staticmethod
    def verify_otp(user, otp):
        stored_otp = cache.get(f'otp:{user.phone}')
        if stored_otp != otp or not stored_otp:
            return None
