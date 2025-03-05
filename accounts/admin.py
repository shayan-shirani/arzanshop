from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from .forms import ShopUserCreationForm, ShopUserChangeForm
# Register your models here.
class AddressInline(admin.TabularInline):
    model = Addresses
    extra = 1
    fields = ['street', 'city', 'state', 'country', 'zip_code']



@admin.register(ShopUser)
class ShopUserAdmin(UserAdmin):
    inlines = [AddressInline]
    model = ShopUser
    add_form = ShopUserCreationForm
    form = ShopUserChangeForm
    list_display = ['first_name', 'last_name','username', 'phone','role','is_active', 'is_staff']
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'username', 'email', 'profile_picture', 'bio')}),
        ('Permissions', {'fields': ('role' ,'is_active','is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {'fields': ('phone', 'password1', 'password2')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'username', 'email')}),
        ('Permissions', {'fields': ( 'role' ,'is_active','is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )


def make_active(modeladmin, request, queryset):
    update_count = 0
    for vendor in queryset:
        if not vendor.is_active:
            vendor.is_active = True
            vendor.save()
            update_count += 1


    if update_count == 1:
        message = 'Vendor is approved'
    else:
        message = f'{update_count} Vendors are approved'

    modeladmin.message_user(request, message)

make_active.short_description = 'Approve Vendors'


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['id','store_name', 'status', 'is_active']
    actions = [make_active]

