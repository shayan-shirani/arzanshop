from rest_framework import serializers
from apps.shop.serializers import ProductSerializer

class CartItemSerializer(serializers.Serializer):
    product = ProductSerializer()
    quantity = serializers.IntegerField()
    price = serializers.IntegerField()
    weight = serializers.IntegerField()


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    discount_amount = serializers.IntegerField()
    post_price = serializers.IntegerField()
    total_price = serializers.IntegerField()
    final_price = serializers.IntegerField()

    def to_representation(self, instance):
        items = [
            {
                'product': ProductSerializer(item['product']).data,
                'quantity': item['quantity'],
                'price': item['price'],
                'weight': item['weight']
            }
            for item in instance
        ]
        return {
            'items': items,
            'discount_amount': instance.get_discount_amount(),
            'post_price': instance.get_post_price(),
            'total_price': instance.get_total_price(),
            'final_price': instance.get_final_price()
        }

class CartActionSerializer(serializers.Serializer):
    product = serializers.IntegerField()

class DiscountSerializer(serializers.Serializer):
    code = serializers.CharField()