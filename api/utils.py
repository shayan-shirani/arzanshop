import random
import redis
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

redis_client = redis.Redis(host='localhost', port=6379, db=1)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(phone, email):
    otp = generate_otp()
    cache.set(f'otp:{phone}', otp, timeout=300)
    send_mail(
        subject="Your OTP Code",
        message=f"Your OTP is: {otp}. It is valid for 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],  # Send to the user's email
        fail_silently=False,
    )
    return otp

def verify_otp(user, otp):
    stored_otp = cache.get(f'otp:{user.phone}')
    if stored_otp != otp or not stored_otp:
        return None