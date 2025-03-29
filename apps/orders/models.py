from django.db import models
from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import ShopUser, Addresses
from apps.shop.models import Product, Discount

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

    def __str__(self):
        return f"order {self.id}"

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]


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


class Subscription(models.Model):
    class PlanType(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        YEARLY = 'yearly', 'Yearly'

    class PlanPrice(models.IntegerChoices):
        MONTHLY = 1000, '1000'
        YEARLY = 2000, '2000'

    user = models.OneToOneField(ShopUser, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=10, choices=PlanType.choices)
    price = models.PositiveIntegerField(choices=PlanPrice.choices, editable=False)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.start_date:
            self.start_date = timezone.now().date()

        if not self.end_date:
            if self.plan == 'monthly':
                self.end_date = self.start_date + timedelta(days=30)
            elif self.plan == 'yearly':
                self.end_date = self.start_date + timedelta(days=365)

        self.price = self.PlanPrice.MONTHLY.value if self.plan == self.PlanType.MONTHLY else self.PlanPrice.YEARLY.value
        super().save(*args, **kwargs)

    def is_valid(self):
        now = timezone.now()
        if self.start_date <= now <= self.end_date and self.is_active:
            return True
        return False

    def discount(self):
        if self.is_active and self.is_valid():
            return 10 if self.plan == self.PlanType.MONTHLY else 20
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()} - {self.price} (Active: {self.is_active})"

