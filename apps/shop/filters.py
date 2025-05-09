from django.db.models import Q

from django_filters import rest_framework as filters

class ProductFilter(filters.FilterSet):
    vendor = filters.NumberFilter(field_name='vendor__id', lookup_expr='exact')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = filters.CharFilter(method='filter_by_category')

    def filter_by_category(self, queryset, name, value):
        return queryset.filter(
            Q(category__name__iexact=value) | Q(category__parent__name__iexact=value)
        )