from django_filters import rest_framework as filters
from apps.shop.models import Product, Category
from django.db.models import Q

class ProductFilter(filters.FilterSet):
    vendor = filters.NumberFilter(field_name='vendor__id', lookup_expr='exact')
    category = filters.CharFilter(method='filter_by_category')
    def filter_by_category(self, queryset, name, value):
        return queryset.filter(
            Q(category__name__iexact=value) | Q(category__parent__name__iexact=value)
        )