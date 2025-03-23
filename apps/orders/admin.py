from django.contrib import admin

from apps.orders.models import Order, OrderItem


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'address', 'first_name', 'last_name', 'phone', 'paid')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass