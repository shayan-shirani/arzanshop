from django.db import models
from accounts.models import ShopUser, Addresses
from shop.models import Product
# Create your models here.
class Order(models.Model):
    buyer = models.ForeignKey(ShopUser, on_delete=models.SET_NULL, related_name='orders_buyer', null=True)
    address = models.ForeignKey(Addresses, on_delete=models.SET_NULL, related_name='orders_address', null=True)
    first_name = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    discount_code = models.CharField(max_length=11, blank=True, null=True)
    discount_amount = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"order {self.id}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_post_cost(self):
        weight = sum(item.get_weight() for item in self.items.all())
        if weight < 1000:
            return 0
        elif 1000 <= weight <= 2000:
            return 30000
        else:
            return 50000

    def get_final_cost(self):
        price = self.get_post_cost() + self.get_total_cost() - self.discount_amount
        return price



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)
    weight = models.PositiveIntegerField(default=0)
    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

    def get_weight(self):
        return self.weight * self.quantity

