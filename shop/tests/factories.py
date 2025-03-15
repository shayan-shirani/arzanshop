import factory
from faker import Faker
from factory.fuzzy import FuzzyDateTime
from shop.models import Product, Category, Discount
from accounts.models import VendorProfile, ShopUser, Addresses
from orders.models import Order, OrderItem
from datetime import datetime, timedelta
from django.utils import timezone
fake = Faker()
class ShopUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShopUser
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Faker('user_name')
    password = factory.Faker('password')
    email = factory.Faker('email')
    phone = factory.LazyAttribute(lambda _: f'09{fake.random_number(digits=9, fix_len=True)}')
    role = ShopUser.Roles.Customer
    is_active = True

class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Addresses
    user = factory.SubFactory(ShopUserFactory)
    street = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state')
    country = factory.Faker('country')
    zip_code = factory.Faker('zipcode')
    is_default = True


class VendorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VendorProfile
    user = factory.SubFactory(ShopUserFactory)
    status = VendorProfile.Status.PENDING
    is_active = False
    store_name = factory.Faker('company')

class ParentCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    name = factory.Faker('word')
    slug = factory.LazyAttribute(
        lambda obj: f'{obj.name.lower()}-{fake.uuid4()[:8]}')


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    name = factory.Faker('word')
    slug = factory.LazyAttribute(
        lambda obj: f'{obj.name.lower()}-{fake.uuid4()[:8]}')
    parent = factory.SubFactory(ParentCategoryFactory)

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    category = factory.SubFactory(CategoryFactory)
    vendor = factory.SubFactory(VendorProfileFactory)
    name = factory.Faker('name')
    slug = factory.LazyAttribute(
        lambda obj: f'{obj.name.lower()}-{fake.uuid4()[:8]}')
    stock = factory.Faker('random_number', digits=3)
    price = factory.Faker('random_number', digits=3)
    description = factory.Faker('text')

class DiscountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Discount
        skip_postgeneration_save = True
    code = factory.Faker('bothify',text='????-########')
    value = factory.Faker('random_int', min=1, max=100)
    description = factory.Faker('text')
    start_date = factory.LazyFunction(lambda: timezone.now() - timedelta(days=10))
    end_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=10))

    @factory.post_generation
    def products(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for product in extracted:
                self.products.add(product)
        else:
            self.products.add(ProductFactory())

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone = factory.LazyAttribute(lambda _: f'09{fake.random_number(digits=9, fix_len=True)}')
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
    quantity = factory.Faker('random_number', digits=1)
    weight = factory.Faker('random_number', digits=2)