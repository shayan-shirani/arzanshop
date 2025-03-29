from django.db import models
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
from autoslug import AutoSlugField

from apps.accounts.models import VendorProfile

class Category(MPTTModel):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return " → ".join(self.get_ancestors(include_self=True).values_list('name', flat=True))

class Product(models.Model):
    name = models.CharField(max_length=100)
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='products')
    slug = AutoSlugField(populate_from='name', unique=True)
    tags = TaggableManager()
    product_picture = models.ImageField(upload_to='product_pictures/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    weight = models.PositiveIntegerField(default=0)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Discount(models.Model):
    products = models.ManyToManyField(Product, related_name='discounts')
    code = models.CharField(max_length=50, unique=True)
    value = models.PositiveIntegerField()
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        if self.start_date <= now <= self.end_date and self.is_active:
            return True
        return False
