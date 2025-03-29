from rest_framework.exceptions import ValidationError

from apps.orders.selectors.subscription_selectors import get_subscription_by_user
from apps.accounts.selectors.address_selectors import get_address_by_id

from apps.orders.models import Order, OrderItem, Subscription
from apps.accounts.models import Addresses


class OrderService:
    def __init__(self, user, cart):
        self.user = user
        self.cart = cart

    def create_order(self, validated_data):
        if not self.cart:
            raise ValidationError('Cart is empty')

        address = self.get_address(validated_data.pop('address_id'))

        discount_code, discount_amount = self.validate_discount(validated_data.pop('discount_code', None))
        order = Order.objects.create(
            buyer=self.user,
            address=address,
            discount_code=discount_code,
            discount_amount=discount_amount,
            **validated_data
        )
        self.add_order_items(order)
        return order

    def get_address(self, address_id):
        try:
            return get_address_by_id(address_id)
        except Addresses.DoesNotExist:
            raise ValidationError(f'Address with ID {address_id} does not exist.')

    def validate_discount(self, discount_code):
        session_discount = self.cart.session.get('discount_code', None)

        if session_discount == discount_code:
            return discount_code, self.cart.get_discount_amount()

        if not discount_code and Subscription.objects.filter(user=self.user).exists():
            subscription = get_subscription_by_user(self.user)
            return subscription.plan, self.cart.subscription_amount(subscription)

        raise ValidationError('Invalid or missing discount code.')

    def add_order_items(self, order):
        for item in self.cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity'],
                weight=item['weight']
            )
