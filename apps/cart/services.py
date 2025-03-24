from apps.shop.models import Product, Discount
from rest_framework.exceptions import NotFound

class CartService:
    @staticmethod
    def add_to_cart(cart, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound('Product does not exist')
        cart.add(product)

    @staticmethod
    def decrease_product_quantity(cart, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound('Product does not exist')
        cart.decrease(product)

    @staticmethod
    def remove_from_cart(cart, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound('Product does not exist')
        cart.remove(product)
