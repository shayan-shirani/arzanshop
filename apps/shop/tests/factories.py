import factory
from faker import Faker

from apps.accounts.tests.factories import VendorProfileFactory

from apps.shop.models import Product, Category

fake = Faker()

class ParentCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('word')


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    parent = factory.SubFactory(ParentCategoryFactory)
    name = factory.Faker('word')


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(CategoryFactory)
    vendor = factory.SubFactory(VendorProfileFactory)
    name = factory.Faker('name')
    stock = factory.Faker('random_number', digits=3)
    price = factory.Faker('random_number', digits=3)
    description = factory.Faker('text')