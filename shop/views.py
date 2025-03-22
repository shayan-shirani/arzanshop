from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from .serializers import *
from .filters import *
from .permissions import *

class ProductsViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsVendor]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer