from django.utils import timezone

from datetime import timedelta

import factory
from faker import Faker

from apps.accounts.tests.factories import VendorProfileFactory

from apps.shop.models import Product, Category, Discount

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


class DiscountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Discount
        skip_postgeneration_save = True

    code = factory.Faker('bothify', text='????-########')
    value = factory.Faker('random_number', digits=2)
    description = factory.Faker('text')
    start_date = timezone.now() - timedelta(days=1)
    end_date = timezone.now() + timedelta(days=1)
    is_active = True

    @factory.post_generation
    def products(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for product in extracted:
                self.products.add(product)
        else:
            self.products.add(ProductFactory())