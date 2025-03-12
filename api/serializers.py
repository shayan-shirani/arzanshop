from rest_framework import serializers
from accounts.models import ShopUser, Addresses, VendorProfile
from orders.models import OrderItem, Order
from shop.models import Product, Category
from cart.cart import Cart
from taggit.serializers import TagListSerializerField, TaggitSerializer
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addresses
        fields = ['street', 'city', 'state', 'country', 'zip_code', 'is_default']
    def create(self, validated_data):
        user = self.context['request'].user
        return Addresses.objects.create(user=user, **validated_data)

class UserRegistrationSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, required=False)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = ShopUser
        fields = ('first_name', 'last_name', 'username', 'phone', 'email', 'password', 'addresses', 'profile_picture')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_phone(self, value):

        if not value.isdigit():
            raise ValidationError('Phone number must be entered in numbers')

        if len(value) != 11:
            raise ValidationError('Phone number must be 11 digits')

        return value

    def create(self, validated_data):
        addresses_data = validated_data.pop('addresses', None)
        password = self.validated_data.pop('password')
        profile_picture = validated_data.pop('profile_picture', None)
        user = ShopUser(**validated_data)
        user.set_password(password)
        if profile_picture:
            user.profile_picture = profile_picture
        user.save()
        if addresses_data:
            for address_data in addresses_data:
                Addresses.objects.create(user=user,**address_data)
        return user


class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = '__all__'
        read_only_fields = ['is_active','status', 'user']

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

class VendorProductsSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)
    class Meta:
        model = VendorProfile
        fields = ['id', 'store_name', 'products']

class ShopUserDetailSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True)
    vendor_profile = VendorProfileSerializer()
    class Meta:
        model = ShopUser
        fields = ('id','first_name', 'last_name', 'username', 'email' ,'role','is_active','is_superuser', 'is_staff' ,'date_joined','addresses', 'vendor_profile')

class ShopUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUser
        fields = ('id', 'first_name')

class ProductCreateSerializer(TaggitSerializer,serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.exclude(parent=None))
    product_picture = serializers.ImageField(required=False, allow_null=True)
    tags = TagListSerializerField()
    class Meta:
        model = Product
        fields = ['category' ,'name', 'description', 'price', 'stock', 'product_picture', 'tags']

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError('Old password is incorrect')
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise ValidationError('Passwords do not match')
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    class Meta:
        model = OrderItem
        fields = ['order', 'product' , 'price' , 'quantity', 'weight']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address_id = serializers.IntegerField(write_only=True)
    total_cost = serializers.SerializerMethodField()
    post_cost = serializers.SerializerMethodField()
    final_cost = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['buyer', 'address_id', 'first_name', 'last_name', 'phone', 'items', 'created', 'updated',
                  'discount_code', 'discount_amount', 'total_cost', 'post_cost', 'final_cost', 'paid']
    def get_total_cost(self, obj):
        return obj.get_total_cost()
    def get_post_cost(self, obj):
        return obj.get_post_cost()
    def get_final_cost(self, obj):
        return obj.get_final_cost()
    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        cart = Cart(request)
        if len(cart) == 0:
            raise serializers.ValidationError('Cart is empty')
        address_id = validated_data.pop('address_id')
        try:
            address = Addresses.objects.get(id=address_id)
        except Addresses.DoesNotExist:
            raise serializers.ValidationError('Address does not exist')
        discount_code = cart.session.get('discount_code', None)
        discount_amount = cart.get_discount_amount()
        order = Order.objects.create(buyer=user, address=address, discount_code=discount_code, discount_amount=discount_amount,**validated_data)
        for item in cart:
            product = item['product']
            OrderItem.objects.create(order=order,
                                     product=product,
                                     price=item['price'],
                                     quantity=item['quantity'],
                                     weight=item['weight'])
        return order