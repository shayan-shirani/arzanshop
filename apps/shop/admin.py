from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from .models import Category, Product
from apps.shop.models import Discount

@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'id')

    mptt_level_indent = 20

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','vendor', 'category', 'name', 'created', 'updated']


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    pass