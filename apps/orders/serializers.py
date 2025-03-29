from rest_framework import serializers
from .models import *
from apps.cart.cart import Cart
from apps.orders.models import Subscription

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
    discount_code = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    final_cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['address_id', 'first_name', 'last_name', 'phone', 'items', 'created', 'updated',
                  'discount_code', 'total_cost', 'post_cost', 'final_cost']

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
        serialized_discount_code = validated_data.pop('discount_code', None)

        if discount_code == serialized_discount_code:
            discount_amount = cart.get_discount_amount()

        if serialized_discount_code:
            subscription_discount = Subscription.objects.get(user=user)
            discount_code = subscription_discount.plan
            discount_amount = subscription_discount.discount()

        else:
            raise serializers.ValidationError('Invalid discount code')

        order = Order.objects.create(buyer=user, address=address, discount_code=discount_code, discount_amount=discount_amount,**validated_data)
        for item in cart:
            product = item['product']
            OrderItem.objects.create(order=order,
                                     product=product,
                                     price=item['price'],
                                     quantity=item['quantity'],
                                     weight=item['weight'])
        return order


class SubscriptionSerializer(serializers.Serializer):
    subscription_type = serializers.CharField()

    def create(self, validated_data):
        user = self.context['request'].user
        subscription_type = validated_data['subscription_type']
        subscription = Subscription.objects.create(user=user, plan=subscription_type)
        return subscription