from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from .models import ShopUser, ShopUserManager

class ShopUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ShopUser
        fields = ('first_name', 'last_name', 'username', 'phone', 'email', 'is_active', 'is_superuser', 'is_staff', 'date_joined', 'role')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if ShopUser.objects.filter(phone=phone).exists():
            raise ValidationError('Phone number already exists')

        if not phone.isdigit():
            raise ValidationError('Phone number must be entered in numbers')

        if len(phone) != 11:
            raise ValidationError('Phone number must be 11 digits')

        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if ShopUser.objects.filter(email=email).exists():
            raise ValidationError('Email already registered')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if ShopUser.objects.filter(username=username).exists():
            raise ValidationError('Username already registered')
        return username

class ShopUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = ShopUser
        fields = ('first_name', 'last_name', 'username', 'phone', 'email', 'is_active', 'is_superuser', 'is_staff', 'date_joined', 'role')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if ShopUser.objects.exclude(id=self.instance.id).filter(phone=phone).exists():
            raise ValidationError('Phone number already exists')

        if not phone.isdigit():
            raise ValidationError('Phone number must be entered in numbers')

        if len(phone) != 11:
            raise ValidationError('Phone number must be 11 digits')

        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if ShopUser.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise ValidationError('Email already registered')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if ShopUser.objects.exclude(id=self.instance.id).filter(username=username).exists():
            raise ValidationError('Username already registered')
        return username