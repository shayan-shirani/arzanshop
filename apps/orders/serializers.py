from rest_framework import serializers

from apps.accounts.selectors.address_selectors import get_address_by_id
from .selectors.subscription_selectors import get_subscription_by_user

from .models import Order, OrderItem, Product, Addresses
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
        fields = [
            'address_id', 'first_name', 'last_name', 'phone', 'items',
            'created', 'updated', 'discount_code', 'total_cost', 'post_cost', 'final_cost'
        ]

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

        address_id = validated_data.pop('address_id', None)

        try:
            address = get_address_by_id(address_id)
        except Addresses.DoesNotExist:
            raise serializers.ValidationError('Address not found')

        session_discount = request.session.get('discount_code', None)
        serialized_discount = validated_data.pop('discount_code', None)

        if session_discount == serialized_discount:
            discount_code = session_discount
            discount_amount = cart.get_discount_amount()
        elif not serialized_discount and Subscription.objects.filter(user=user).exists():
            subscription = get_subscription_by_user(user)
            discount_code = subscription.plan
            discount_amount = cart.subscription_amount(subscription)
        else:
            discount_code = None
            discount_amount = 0

        order = Order.objects.create(
            buyer=user,
            address=address,
            discount_code=discount_code,
            discount_amount=discount_amount,
            **validated_data
        )

        for item in cart:
            product = item['product']
            OrderItem.objects.create(
                order=order,
                product=product,
                price=item['price'],
                quantity=item['quantity'],
                weight=item['weight'],
            )

        return order


class SubscriptionSerializer(serializers.Serializer):
    subscription_type = serializers.CharField()

    def create(self, validated_data):
        user = self.context['request'].user
        subscription_type = validated_data['subscription_type']
        subscription = Subscription.objects.create(user=user, plan=subscription_type)
        return subscription