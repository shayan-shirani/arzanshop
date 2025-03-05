from django.contrib import admin
from .models import Category, Product
from mptt.admin import MPTTModelAdmin

from shop.models import Discount


# Register your models here.

@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'id')
    prepopulated_fields = {'slug': ('name',)}
    mptt_level_indent = 20

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'category', 'name', 'created', 'updated']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    pass