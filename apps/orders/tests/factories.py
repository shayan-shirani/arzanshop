from django.utils import timezone

from datetime import timedelta
import factory
from faker import Faker

from apps.orders.models import Order, OrderItem, Subscription

from apps.accounts.tests.factories import ShopUserFactory, AddressFactory
from apps.shop.tests.factories import ProductFactory

fake = Faker()

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone = factory.LazyFunction(lambda: f'0913{fake.random_number(digits=7, fix_len=True)}')
    address = factory.SubFactory(AddressFactory)
    buyer = factory.SubFactory(ShopUserFactory)
    transaction_id = factory.Faker('uuid4')
    paid = False


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    price = factory.Faker('random_number', digits=3)
    quantity = factory.Faker('random_number', digits=2)
    weight = factory.Faker('random_number', digits=2)


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    buyer = factory.SubFactory(ShopUserFactory)
    plan = Subscription.PlanType.MONTHLY
    paid = True
    is_active = True
    transaction_id = factory.Faker('uuid4')