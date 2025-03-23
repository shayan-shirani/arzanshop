from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from apps.shop.models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['parent','name']

    def get_parent(self, obj):
        return obj.parent.name if obj.parent else None

class ProductSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField()
    category = CategorySerializer()
    product_picture = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Product
        fields = ['id', 'category' ,'name', 'description', 'price', 'stock', 'product_picture', 'tags']

class ProductCreateSerializer(TaggitSerializer,serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.exclude(parent=None))
    product_picture = serializers.ImageField(required=False, allow_null=True)
    tags = TagListSerializerField()
    class Meta:
        model = Product
        fields = ['category' ,'name', 'description', 'price', 'stock', 'weight','product_picture', 'tags']
    def create(self, validated_data):
        user = self.context['request'].user
        return Product.objects.create(vendor=user.vendor_profile, **validated_data)