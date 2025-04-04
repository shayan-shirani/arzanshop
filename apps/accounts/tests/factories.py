import factory
from faker import Faker

from apps.accounts.models import ShopUser, Addresses, VendorProfile

fake = Faker()

class ShopUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShopUser

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Faker('user_name')
    password = factory.Faker('password')
    email = factory.Faker('email')
    phone = factory.LazyFunction(lambda: fake.random_number(digits=5, fix_len=True))
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
    zip_code = factory.LazyFunction(lambda: int(fake.random_number(digits=5, fix_len=True)))
    is_default = True


class VendorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VendorProfile
    user = factory.SubFactory(ShopUserFactory)
    status = VendorProfile.Status.PENDING
    is_active = False
    store_name = factory.Faker('company')