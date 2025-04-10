from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class ShopUserManager(BaseUserManager):
    def create_user(self, username, phone, email , password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have an username')

        if not phone:
            raise ValueError('Users must have an phone')

        if not email:
            raise ValueError('Users must have an email')

        email = self.normalize_email(email)
        user = self.model(username=username, phone=phone, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone, email , password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')

        return self.create_user(username, phone, email, password, **extra_fields)


class ShopUser(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        VENDOR = 'vendor', 'Vendor'
        Customer = 'customer', 'Customer'

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.Customer)
    profile_picture = models.ImageField(upload_to='profile_picture/%y/%m/%d', null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'phone']
    objects = ShopUserManager()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Shop User'
        verbose_name_plural = 'Shop Users'


class Addresses(models.Model):
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    zip_code = models.IntegerField()
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.street}, {self.city}, {self.country}'

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'


class VendorProfile(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.OneToOneField(ShopUser, on_delete=models.CASCADE, related_name='vendor_profile')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    store_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def approve(self):
        self.status = VendorProfile.Status.APPROVED
        self.is_active = True
        self.store_name = self.store_name
        self.user.role = ShopUser.Roles.VENDOR
        self.user.save()
        self.save()

    def reject(self):
        self.status = VendorProfile.Status.REJECTED
        self.save()

    def __str__(self):
        return self.store_name if self.store_name else None

    class Meta:
        verbose_name = 'Vendor Profile'
        verbose_name_plural = 'Vendor Profiles'