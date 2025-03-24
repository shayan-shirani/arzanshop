from apps.shop.models import Product, Discount

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 1, 'price': product.price, 'weight': product.weight}
        else:
            if self.cart[product_id]['quantity'] < product.stock:
                self.cart[product_id]['quantity'] += 1
        self.save()

    def decrease(self, product):
        product_id = str(product.id)
        if self.cart[product_id]['quantity'] > 1:
            self.cart[product_id]['quantity'] -= 1
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if self.cart[product_id]['quantity'] > 0:
            del self.cart[product_id]
        self.save()

    def clear(self):
        del self.session['cart']
        self.save()

    def apply_discount(self, code):
        try:
            discount = Discount.objects.get(code=code)
        except Discount.DoesNotExist:
            return {'detail': 'Invalid discount code'}
        if not discount.is_valid():
            return {'detail': 'This discount code has expired'}
        self.session['discount_code'] = code
        self.save()
        return {'detail': 'discount code Successfully applied'}

    def get_discount_amount(self):
        code = self.session.get('discount_code')
        try:
            discount = Discount.objects.get(code=code)
        except Discount.DoesNotExist:
            return 0
        if not discount.is_valid():
            return 0
        return discount.value / 100 * self.get_total_price()

    def get_post_price(self):
        weight = sum(item['weight'] * item['quantity'] for item in self.cart.values())
        if weight < 1000:
            return 0
        elif 1000 <= weight <= 2000:
            return 30000
        else:
            return 50000

    def get_total_price(self):
        price = sum(item['price'] * item['quantity'] for item in self.cart.values())
        return price

    def get_final_price(self):
        return self.get_total_price() + self.get_post_price() - self.get_discount_amount()

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product
        for item in self.cart.values():
            yield item

    def save(self):
        self.session.modified = True