import factory
from faker import Faker
from shop.models import Product, Category, Discount
from accounts.models import VendorProfile, ShopUser, Addresses


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
    name = 'Root Category'
    slug = 'root-category'

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    name = 'Child Category'
    slug = 'child-category'
    parent = factory.SubFactory(ParentCategoryFactory)

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    vendor = factory.SubFactory(VendorProfileFactory)
    name = factory.Faker('name')
    stock = factory.Faker('random_number', digits=3)
    price = factory.Faker('random_number', digits=3)
    description = factory.Faker('text')

class DiscountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Discount
    product = factory.SubFactory(ProductFactory)
    code = factory.Faker('pystr', min_chars=5, max_chars=10)
    discount = factory.Faker('random_number', digits=2)
    description = factory.Faker('text')
    start_date = factory.Faker('date')
    end_date = factory.Faker('date')